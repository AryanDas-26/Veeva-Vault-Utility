# Veeva-Vault-Utility

The python project is a GUI utility designed to facilitate various tasks within Veeva Vault, a content management platform. Primarily, it enables users to perform tasks such as bulk document deletion efficiently. The utility provides a graphical interface that allows users to interact with Veeva Vault functionalities without needing to directly access the platform's backend or API.

## How-to-use: Bulk_Delete_Documents

1. Open the file "Veeva_Bulk_Delete_Documents_GUI.exe".
2. Select the Vault Subdomain and API Version from dropdown, select the Username and Password and click on "Authenticate".
3. If the Authentication is successful, then you would get the "Authentication Successful" prompt in the console, along with the Session ID.
4. Click on "View Admin Console".
5. From the Admin Console, navigate to "Bulk Document Deletion".
6. Select the CSV file which consists of the Identifier (id or external_id) of the Documents to be deleted {refer to file "Document_Del.csv"}.
7. Select the Identifier of the documents and Buffer Time (time between each API call) and click on "Bulk Delete Documents".
8. Status of the deletion task would be visible in the Console.
9. Once the task is completed, the status of all the deleted documents would be stored in CSV files in batches where the maximum size is 500 as permited by Veeva Rest API (refer to file "Deletion_Response_Batch_1.csv")
10. To view the status files, click on "View Status Files".
11. To exit the utility, click on "Exit" button or close directly.

### Snippet:

![image](https://github.com/AryanDas-26/Veeva-Vault-Utility/assets/126672132/ac9fb148-0204-4dbf-aa6f-abd881016aa7)
