from SimpleLTVCustomers import *
import argparse, os, json


def main():
    ltv = SimpleLTVCustomers()
    input_data = None
    filename = None
    no_of_customers = None
    input_data_dict = {}

    parser = argparse.ArgumentParser(
        description='''This code is calulating simple LTV using the equation: 52(a) x t''',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-InFile', '--InFile', default='InFile', action="store", type=str, help='Please provide event data file name.')
    parser.add_argument('-numCust', '--numCust', default='noCust', action="store", type=int, help='Please provide top number of customers in integer value to calculate highest Simple Lifetime Value.')
    args = vars(parser.parse_args())

    filename = args['InFile']
    no_of_customers = args['numCust']

    try:
        if os.path.isfile(filename) == True:
            with open(filename,"r") as inputfile:
                # decoding the Input JSON to dictionay
                input_data = json.load(inputfile)
        else:
            print("Please provide a valid input file path.")
    except Exception as err:
        raise err

    # Calculate top x customers with the highest Simple Lifetime Value from data D.
    status = ltv.TopXSimpleLTVCustomers(x=no_of_customers, D=ltv.Ingest(e=input_data, D=input_data_dict))
    '''
    if status:
        print("The top x customers with the highest Simple Lifetime Value are successfully calculated and populated in output.txt file under output directory.")
    else:
        print("Somethign went wrong while calculating top x customers with the highest Simple Lifetime Value. ")
    '''



main()