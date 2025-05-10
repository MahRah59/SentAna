from pyNumbers import Numbers

# Load the .numbers file
numbers_file = Numbers('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/Test_Data/testData_1')

# Convert to CSV
numbers_file.to_csv('output.csv')
