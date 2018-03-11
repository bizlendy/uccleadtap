# -*- coding: utf-8 -*-
import csv
from scrapy import Spider
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser


class Appext20Spider(Spider):
    name = 'appext20'
    allowed_domains = ['appext20.dos.ny.gov']

    def start_requests(self):
        with open('UCC NYS File Numbers.csv', 'rb') as f:
            reader = csv.reader(f)
            for line in reader:
                p_filenum = line[0]

                data = {'p_filenum': p_filenum,
                        'p_year': p_filenum[0:4]}

                yield FormRequest('https://appext20.dos.ny.gov/pls/ucc_public/web_searches.file_num_search',
                                  formdata=data,
                                  meta={'p_filenum': p_filenum,
                                        'p_year': p_filenum[0:4]},
                                  callback=self.parse)

    def parse(self, response):
        if 'No records found matching' in response.body:
            yield {'UCC_FileNumber': response.meta['p_filenum'],
                   'UCC_FileYear': response.meta['p_year'],
                   'results': 'No records found matching'}
        else:
            debtor_found = False
            first_table_dict = {}

            table = response.xpath('//*[@align="CENTER"]')[1]
            trs = table.xpath('.//tr')[:-1]
            for debtor_counter, tr in enumerate(trs):
                debtor_counter += 1

                second_column = tr.xpath('.//td[2]/font/b/text()').extract_first()

                if second_column == 'Debtors:':
                    debtor_name = tr.xpath('.//td[3]/font/b/text()').extract_first()
                    debtor_address = tr.xpath('.//td[4]/font/b/text()').extract_first()

                    first_table_dict['CompanyName' + str(debtor_counter)] = debtor_name
                    first_table_dict['CompanyAddress' + str(debtor_counter)] = debtor_address

                    debtor_found = True

                if not second_column and debtor_found is True:
                    debtor_name = tr.xpath('.//td[3]/font/b/text()').extract_first()
                    debtor_address = tr.xpath('.//td[4]/font/b/text()').extract_first()

                    first_table_dict['CompanyName' + str(debtor_counter)] = debtor_name
                    first_table_dict['CompanyAddress' + str(debtor_counter)] = debtor_address

                if second_column == 'Secured Party Names:':
                    break

            # secured_party_names_found = False
            # secured_party_counter = 0

            # table = response.xpath('//*[@align="CENTER"]')[1]
            # trs = table.xpath('.//tr')[:-1]
            # for tr in trs:
            #     second_column = tr.xpath('.//td[2]/font/b/text()').extract_first()

            #     if second_column == 'Secured Party Names:':
            #         secured_party_counter += 1

            #         secured_party_name = tr.xpath('.//td[3]/font/b/text()').extract_first()
            #         secured_party_address = tr.xpath('.//td[4]/font/b/text()').extract_first()

            #         first_table_dict['Secured Party Name ' + str(secured_party_counter)] = secured_party_name
            #         first_table_dict['Secured Party Address ' + str(secured_party_counter)] = secured_party_address

            #         secured_party_names_found = True

            #     if not second_column and secured_party_names_found is True:
            #         secured_party_counter += 1

            #         secured_party_name = tr.xpath('.//td[3]/font/b/text()').extract_first()
            #         secured_party_address = tr.xpath('.//td[4]/font/b/text()').extract_first()

            #         first_table_dict['Secured Party Name ' + str(secured_party_counter)] = secured_party_name
            #         first_table_dict['Secured Party Address ' + str(secured_party_counter)] = secured_party_address

            second_table_dict = {}
            second_table = response.xpath('//*[@align="CENTER"]')[-1]
            trs = second_table.xpath('.//tr')[1:]
            counter = 1
            for tr in trs:
                file_no = tr.xpath('.//td[1]/font/text()').extract_first()
                file_date = tr.xpath('.//td[2]/font/text()').extract_first()
                lapse_date = tr.xpath('.//td[3]/font/text()').extract_first()
                filing_type = tr.xpath('.//td[4]/font/text()').extract_first()
                pages = tr.xpath('.//td[5]/font/text()').extract_first()
                image = tr.xpath('.//td[6]/font/a/@href').extract_first()

                if 'Financing Statement' in filing_type:
                    second_table_dict['FileNumber' + str(counter)] = file_no
                    second_table_dict['FileDate' + str(counter)] = file_date

                    counter += 1

                # second_table_dict['File no. ' + str(counter)] = file_no
                # second_table_dict['File Date ' + str(counter)] = file_date
                # second_table_dict['Lapse Date ' + str(counter)] = lapse_date
                # second_table_dict['Filing Type ' + str(counter)] = filing_type
                # second_table_dict['Pages ' + str(counter)] = pages
                # second_table_dict['Image ' + str(counter)] = image

            secured_party_name = response.xpath(
                '//b[text()="Secured Party Names:"]/following::b/text()').extract_first()

            items = {'SecuredPartyName': secured_party_name,
                     'UCC_FileNumber': response.meta['p_filenum'],
                     'UCC_FileYear': response.meta['p_year']}

            yield dict(first_table_dict.items() + second_table_dict.items() + items.items())
