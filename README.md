# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource                       | Service Tier                                                                         | Monthly Cost |
| -------------------------------------| ------------------------------------------------------------------------------------ |  ----------- |
| Azure Postgres Database              | Burstable, B1ms: 1 vCores, 2 GiB RAM, 128 GiB storage, P10 (500 IOPS);               | ~ 27$        |
| Azure Service Bus                    | Basic: Max Message Size 256 KB - 1M OPS                                              | ~ 0.05$      |
| Azure Storage Account                | StorageV2 (general purpose v2)                                                       | ~ 0.05$      |    
| Azure Function App                   | Premium V2: 14 GB(0,532/h)                                                           | ~ 338$       |
| Azure Web App                        | D1: 1 GB memory, 240 CPU minutes / day                                               | ~ 270$       |
| Total                                | Total cost                                                                           | ~ 27.1$      |
| -------------------------------------| -------------------------------------------------------------------------------------|--------------|

## Architecture Explanation

Reasons for choosing my architecture for both Azure Web App and Azure Functions:
- Azure PostgreSQL Database: I chose Postgres Database because it is fully managed database solution offering features such as backup, recovery, security, and monitoring. It’s designed to scale seamlessly to accommodate increasing data demands.
- Azure Service Bus: Provides robust service continuity and fault tolerance, supporting queuing and messaging to efficiently handle workflows and inter-service communication. For this project, I’ve configured it for sending emails, using a basic setup to manage costs.
- Azure Storage Account: Offers versatile storage solutions for unstructured data, including blobs, files, queues, and tables. It’s easy to manage and provides a cost-effective storage solution.
- Azure Web App and Azure Fuction App: In this case, I find that the main consideration is appropriate usage according to project requirements, which informs my choice of configuration. I plan to upgrade configurations in the future as usage demands increase. This implementation is currently effective and offers a solid foundation.

