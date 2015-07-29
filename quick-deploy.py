#!/usr/bin/env python

import sys
import os
import subprocess

# Constants
elasticbeanstalk_directory = ".elasticbeanstalk"
pom_xml = "pom.xml"
target_directory = "target"

# Get rid of the script name from the parameter list
script_name = sys.argv.pop(0)

# Show the expected arguments and exit with the provided error message
def show_arguments_and_exit(error_message):
  print("%s elastic_beanstalk_configuration_directory root_application_directory [application1_directory application1_name] [application2_directory application2_name] ..." % script_name)
  sys.exit(error_message)

# Executes a command in a specific directory.  If no directory is specified it defaults to the directory in which the script was invoked.  Returns all STDOUT and STDERR data.
def execute_command_in_directory(cmd, directory="."):
  child = subprocess.Popen(cmd, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = child.communicate()

  # Return both STDOUT and STDERR to the caller
  return out, err

def get_list_of_war_files(directory):
  # Get the list of WAR files
  results = [ f for f in os.listdir(directory) if (os.path.isfile(os.path.join(directory,f)) and f.endswith(".war")) ]

  # Prepend the directory to each entry and return it
  return [ directory + "/" + entry for entry in results ]

# Exits with a provided error message if err is not empty.  err must be a string and must not be None.
def print_error_and_exit_if_necessary(err, message):
  if err != "":
    print(err)
    sys.exit(message)

# Builds a Java application using Maven and moves the generated WAR file to a specified location
def build_and_move_application(application_directory, application_name):
  # Make sure the application has a pom.xml
  if os.path.isfile(application_directory + "/" + pom_xml) == False:
    sys.exit("There is no pom.xml in %s" % application_directory)

  # Always clean, compile, run tests, and package up the WAR file
  cmd = ["mvn", "clean", "compile", "test", "war:war"]
  out, err = execute_command_in_directory(cmd, application_directory)

  # Make sure build was successful
  print_error_and_exit_if_necessary(err, "Build of %s failed" % application_directory)

  # Make sure WAR file exists
  war_files = get_list_of_war_files(application_directory + "/" + target_directory)

  if (war_files is None) or len(war_files) == 0:
    sys.exit("No WAR files generated from build of %s" % application_directory)

  if len(war_files) > 1:
    sys.exit("More than one WAR file generated from build of %s" % application_directory)

  # Move WAR file to proper location
  original_name = war_files[0]
  new_name = environment_directory + "/" + application_name + ".war"
  os.rename(original_name, new_name)

# Get command-line parameters
#   First parameter is the directory that contains the .elasticbeanstalk configuration
#   Second parameter is the directory that contains the ROOT application
#   Each pair of parameters after that is a directory followed by the path desired on the EC2 container

# Make sure parameter count is non-zero
if len(sys.argv) == 0:
  show_arguments_and_exit("You didn't specify any parameters")

# Make sure parameter count is even
if (len(sys.argv) % 2) != 0:
  show_arguments_and_exit("You didn't specify the correct number of parameters")

# Make sure Elastic Beanstalk environment exists
environment_directory = sys.argv.pop(0)

if os.path.isdir(environment_directory) == False:
  sys.exit("Specified Elastic Beanstalk environment directory does not exist")

if os.path.isdir(environment_directory + '/' + elasticbeanstalk_directory) == False:
  sys.exit("Specified Elastic Beanstalk environment directory does not contain an %s directory" % elasticbeanstalk_directory)

cmd = ["eb", "status"]
out, err = execute_command_in_directory(cmd, environment_directory)

print_error_and_exit_if_necessary(err, "'eb status' returned an error in %s" % environment_directory)

# Blow away everything except .elasticbeanstalk and .gitignore
cmd = ["sh", "-c", "ls | grep -v .elasticbeanstalk | grep -v .gitignore | grep -v .ebextensions | xargs rm -r"]
out, err = execute_command_in_directory(cmd, environment_directory)

# Make sure ROOT application is there, build it, and move it into place
root_application_directory = sys.argv.pop(0)
root_application_name = "ROOT"

print("Building ROOT application...")
build_and_move_application(root_application_directory, root_application_name)
print("ROOT application built")

# Loop through the remaining applications, build them, and move them into place
while len(sys.argv) > 0:
  application_directory = sys.argv.pop(0)
  application_name = sys.argv.pop(0)
  print("Building %s application..." % application_name)
  build_and_move_application(application_directory, application_name)

# Get the list of built applications
war_files = get_list_of_war_files(environment_directory)

if (war_files is None) or (len(war_files) == 0):
  sys.exit("No WAR files built.  This should never happen.  Please report this as a bug!")

if len(war_files) == 1:
  # Only one application built, expand it
  war_filename = war_files[0]
  cmd = ["unzip", war_filename, "-d", environment_directory]
  out, err = execute_command_in_directory(cmd)

  print_error_and_exit_if_necessary(err, "Failed to unzip single application %s" % war_filename)

# Deploy everything
cmd = ["eb", "deploy"]
directory = environment_directory
print("Deploying application.  This can take a long time.")
out, err = execute_command_in_directory(cmd, directory)

print_error_and_exit_if_necessary(err, "There was an error during 'eb deploy'")
print("Application deployed")
