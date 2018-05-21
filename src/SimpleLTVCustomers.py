"""
Created on April, 2018
__author__: sshirke

Description: One way to analyze acquisition strategy and estimate marketing cost is to calculate the Lifetime Value (“LTV”) of a customer.
Simply speaking, LTV is the projected revenue that customer will generate during their lifetime. A simple LTV can be calculated using the following equation: 52(a) x t.
Where a is the average customer value per week (customer expenditures per visit (USD) x number of site visits per week) and t is the average customer lifespan.
The average lifespan for Shutterfly is 10 years.

A program that ingests event data and implements one analytic method, to calculate the Lifetime Value (“LTV”) of a customer.

**Ingest(e, D) :
Given event e, update data D

**TopXSimpleLTVCustomers(x, D):

Return the top x customers with the highest Simple Lifetime Value from data D.

Please note that the timeframe for this calculation should come from D. That is, use the data that was ingested into D to calculate the LTV to frame the start and
end dates of your LTV calculation. You should not be using external data (in particular "now") for this calculation.

"""

import logging
from HelperClasses import Customers,Visits,Images,Orders
from collections import defaultdict


class SimpleLTVCustomers(object):

    def __init__(self):
        # set up logging to file - see previous section for more details
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)-2s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='./src/logs/SimpleLTV.log',
                            filemode='w')

        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)


    def Ingest(self, e, D):
        """
        Given event e, update data D (ingests event data)
        :param e: Event data
        :param D: Data Dictionary
        :return: update data D
        """

        for item in e:
            if item['type'] == 'CUSTOMER':
                key = item['key']
                customer = Customers(key=key, verb=item['verb'], event_time=item['event_time'], last_name=item['last_name'], adr_city=item['adr_city'],
                                        adr_state=item['adr_state'])
                if key not in D:
                    D[key] = defaultdict(list)  # adding customer details to dictionary with list
                D[key]['CUSTOMER'].append(customer)

            elif item['type'] == 'SITE_VISIT':
                customer_id = item['customer_id']
                visit = Visits(key=item['key'], verb=item['verb'], event_time= item['event_time'], customer_id=customer_id, tags= item['tags'])
                D[customer_id]['SITE_VISIT'].append(visit)  # appending site visit  details to dictionary

            elif item['type'] == 'IMAGE':
                customer_id = item['customer_id']
                image = Images(key=item['key'], verb=item['verb'], event_time=item['event_time'], customer_id=customer_id,
                                      camera_make=item['camera_make'], camera_model=item['camera_model'])
                D[customer_id]['IMAGE'].append(image)  # appending image upload details to dictionary

            elif item['type'] == 'ORDER':
                customer_id = item['customer_id']
                order = Orders(key=item['key'], verb=item['verb'], event_time=item['event_time'], customer_id=customer_id, total_amount=item['total_amount'])
                D[customer_id]['ORDER'].append(order)  # appending order details to dictionary
            else:
                print('Input is not valid!')
                exit(1)

        return D


    def TopXSimpleLTVCustomers(self,x, D):
        """
        An analytic method to calculate highest Simple Lifetime Value
        :param x: top 'x' number of customers
        :param D: Data Dictionary
        :return: Return the top x customers with the highest Simple Lifetime Value from data D.

        Formula: 52(a) x t
        a is the average customer value per week (customer expenditures per visit (USD) x number of site visits per week)
        t is the average customer lifespan. The average lifespan for Shutterfly is 10 years.

        """
        from datetime import datetime, timedelta
        total_amount = 0
        no_of_visit = 0
        t = 10

        top_cust_highest_lifetime_value = {}  # dictionary to hold customer id and LTV value for top X customer

        status = True
        for item in D.keys():
            order = D[item].get('ORDER', None)
            if order is not None:
                for o in order:
                    # total amount spent by customer
                    total_amount = total_amount + float(o.total_amount.split(' ')[0].strip())
            else:
                print("Input data has no site visit information.")
                status = False

            visit = D[item].get('SITE_VISIT', None)
            if visit is not None:
                no_of_visit = len(visit)
            else:
                print("Input data has no site visit information.")
                status = False

            # Logic to get the number of weeks
            cust_event_time = D[item].get('CUSTOMER')[0].event_time
            cust_event_time_date = datetime.strptime(cust_event_time, '%Y-%m-%dT%H:%M:%S.%fZ').date()

            firstweek = cust_event_time_date - timedelta(days=cust_event_time_date.weekday())  # Assuming the given date in the file as start week and taking the starting week of the customer
            currweek = datetime.now().date() - timedelta(days=datetime.now().date().weekday())  # Current week
            total_no_weeks = int(abs((firstweek - currweek).days)) / 7

            if total_no_weeks == 0:  # check if visit is current week
                total_no_weeks = 1

            # calculating the avaerage part 'a'
            if no_of_visit > 0:  # checking this inorder to avoid divide by zero error caused by no_of_visit
                avg_cust_amount = total_amount / no_of_visit
                site_visit_per_week = no_of_visit / total_no_weeks
                a = avg_cust_amount * site_visit_per_week
                lifetime_value = 52 * a * t
            else:
                lifetime_value = 0
            top_cust_highest_lifetime_value[item] = lifetime_value


        # sorting the dictionary and printing the top X customers
        simple_lifetime_value = []
        logging.info("The following is the Simple Livetime Value for Shutterfly customers. ")
        if x > len(D):
            print('The value of top customers(x) is greater than number of customers available in the input file. Therefore, calculating LTV for all the customers in the file.')
            x = len(D)
        for cust_id in sorted(top_cust_highest_lifetime_value, key=top_cust_highest_lifetime_value.get, reverse=True):
            simple_lifetime_value.append((cust_id, top_cust_highest_lifetime_value.get(cust_id)))

        top_cust_ltv = open("./output/output.txt","w")
        logging.info("Customer ID \t Simple Lifetime Value")
        #print("Customer ID \t Simple Lifetime Value")
        top_cust_ltv.write("Customer ID \t Simple Lifetime Value \n")

        for cnt in range(0, x):
            top_cust_ltv.write("{} \t {} \n".format(str(simple_lifetime_value[cnt][0]), str(simple_lifetime_value[cnt][1])))
            #print("{} \t {}".format(str(simple_lifetime_value[cnt][0]), str(simple_lifetime_value[cnt][1])))
            logging.info("{} \t {}".format(str(simple_lifetime_value[cnt][0]), str(simple_lifetime_value[cnt][1])))
        top_cust_ltv.close()
        return status