## Life Made Easier
Refer to the [Scripts](README.md#scripts) in the [Readme](README.md) for single line commands to build, push, and deploy your application.

IF you're looking for more detail on how to run your application locally with Docker, or deploy your application to Google Cloud, or if you find you need to authenticate - read on.

### Run Locally with Docker
The advantage of running your application in Docker is that you can ensure that your application runs the same way locally as it does in the cloud.

When you're ready to run locally, start your application by running:
`docker compose up --build`.

Your application will be available at http://localhost:8000.

(To run locally on your machine without docker [click here](README.md#locally-on-your-machine))
_________________

### Deploying to Google Cloud
After ensuring that docker and docker-compose are installed - and that docker-desktop is running - you can build and run your application by running:
1. Setup gcloud auth: 
  ```
  gcloud auth login
  ```
2. Set your project: 
```
gcloud config set project calarmhelp
```
3. Set your region: 
```
gcloud config set compute/region us-east1
```
4. Set your registry: 
```
gcloud auth configure-docker gcr.io
```
5. Build your image: 
Be careful to include the `.` at the end of the command.
It is not a typo, it is a reference to the current directory.
```
docker build -t gcr.io/calarmhelp/<name-you-pick>:latest .
```
6. Push your image: 
Notice, there is no further reference to the current directory, hence no `.` is needed.
```
docker push gcr.io/calarmhelp/<name-you-picked-in-the-previous-step>:latest
```
7. Deploy your image: 
```
gcloud run deploy --image gcr.io/calarmhelp/<name-you-picked-in-the-previous-step>:latest --platform managed --region us-east1 --allow-unauthenticated
```

_________________
README.md
## References
- [Start](README.md#Start): Instructions for starting the application.
- [Docker's Python Guide](https://docs.docker.com/language/python/): Official guide for using Python with Docker.
- [Docker: Getting Started](https://docs.docker.com/get-started/workshop/): Comprehensive guide on building and pushing Docker images.
- [Docker Compose: How It Works](https://docs.docker.com/compose/compose-application-model/): Explanation of Docker Compose functionality.
- [Google Cloud Run](https://cloud.google.com/run/docs/deploying): Documentation for deploying applications to Google Cloud Run.
- [Google Cloud Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation-with-other-providers): Guide on integrating other identity providers with Google Cloud.
- [Google Cloud Local Testing](https://cloud.google.com/kubernetes-engine/enterprise/knative-serving/docs/testing/local): Instructions for local testing with Google Cloud.