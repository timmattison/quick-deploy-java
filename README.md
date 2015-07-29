# quick-deploy-java

This is a Python script that makes it easier to deploy Java applications to Elastic Beanstalk.  It supports deploying a single application or multiple applications into a single instance.

## CAUTION

This script **_deletes everything in the parent directory of your `.elasticbeanstalk` directory_** except for `.gitignore`, `.ebextensions`, and `.elasticbeanstalk`.

This script has only been tested on very simple applications.  You run this code at your own peril if you do not understand what is going on.

## Syntax

```
quick-deploy.py elastic_beanstalk_configuration_directory root_application_directory [application1_directory application1_name] [application2_directory application2_name] ...
```

Required parameters:

- `elastic_beanstalk_configuration_directory` is the directory that contains the `.elasticbeanstalk` directory for the application you want to deploy.  NOTE: This is not the `.elasticbeanstalk` directory itself!  This is its parent directory.
- `root_application_directory` is the directory that contains the Java project you want to be deployed as the ROOT application in Tomcat.

Optional parameter set:

- `applicationX_directory` is the directory that contains a Java project you want deployed at a specific path
- `applicationX_name` is the path for the project in `applicationX_directory`

You may include zero or more optional parameter sets.

## Example

```
quick-deploy.py three_apps root_app app1 path1 app2 path2
```

This will look for your `.elasticbeanstalk` configuration in the directory `three_apps`, build `root_app`, `app1`, and `app2` using Maven, and then deploy all three in each EC2 instance running `three_apps`.

`root_app` will be accessible at the root path.

`app1` will be accessible at the `/path1` path.

`app2` will be accessible at the `/path2` path.