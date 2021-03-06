clean:		## delete pycache, build files
	@rm -rf build build.zip
	@rm -rf __pycache__

fetch-dependencies:		## download chromedriver, headless-chrome to `./bin/`
	@mkdir -p bin/

	# Get chromedriver
	@if [ ! -e chromedriver.zip ]; \
		then curl -SL https://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip > chromedriver.zip ; \
	fi;	
	unzip -o chromedriver.zip -d bin/

	# Get Headless-chrome
	@if [ ! -e headless-chromium.zip ]; \
		then curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-55/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip ; \
		fi;
	unzip -o headless-chromium.zip -d bin/


## prepares build.zip archive for AWS Lambda deploy 
lambda-build: clean 
	mkdir build build/lib
	cp -r src build/.
	cp -r bin build/.
	pip install -r requirements.txt -t build/lib/.
	rm -r *.whl *.dist-info __pycache__
	cp -r lib build/.
	cd build; zip -9qr build.zip .
	cp build/build.zip .
	rm -rf build

## create CloudFormation stack with lambda function and role.
## usage:	make BUCKET=your_bucket_name create-stack 
create-stack: 
	aws s3 cp build.zip s3://${BUCKET}/src/ScreenshotFunction.zip
	aws cloudformation create-stack --stack-name LambdaScreenshot --template-body file://cloud.yaml --parameters ParameterKey=BucketName,ParameterValue=${BUCKET} --capabilities CAPABILITY_IAM