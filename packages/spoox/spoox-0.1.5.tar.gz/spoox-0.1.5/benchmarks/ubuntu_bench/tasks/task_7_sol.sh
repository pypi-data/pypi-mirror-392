# 1. copy sample solution java project (includes pom.xml and all expected java implementations)
rm -rf ~/jf_program
cp -R /opt/jf_program_sample_solution/jf_program/ ~/

# 2. install and execute maven
sudo apt-get install -y default-jdk maven

# 3. execute maven (not required)
#cd ~/jf_program
#mvn test