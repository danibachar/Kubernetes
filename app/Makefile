APP_IMAGE_TAG=$(shell git log -n 1 --pretty=format:%h ..)
APP_IMAGE=python:3.5.3:$(APP_IMAGE_TAG)

ESP_IMAGE_TAG=1.3
ESP_IMAGE=gcr.io/endpoints-release/endpoints-runtime:$(ESP_IMAGE_TAG)

define generate-deployment-dev
	sed -e 's%{{APP_IMAGE}}%$(APP_IMAGE)%g;s%{{ESP_IMAGE}}%$(ESP_IMAGE)%g' kube/dev/deployment.yaml
endef

define generate-deployment-test
	sed -e 's%{{APP_IMAGE}}%$(APP_IMAGE)%g' test/job-test.yaml
endef

deploy-dev: build-dev
	kubectl apply -f ../config/esp-nginx-dev.yaml
	kubectl apply -f kube/dev/config.yaml
	kubectl apply -f kube/dev/service.yaml
	$(call generate-deployment-dev) | kubectl apply -f -

delete-dev-deploy:
	$(call generate-deployment-dev) | kubectl delete -f -
	kubectl delete -f kube/dev/service.yaml

build-dev:
	gcloud docker -- pull $(APP_IMAGE) || (docker build -f kube/dev/Dockerfile -t $(APP_IMAGE) .. && gcloud docker -- push $(APP_IMAGE))

deploy-local: build-local-dev
	kubectl apply -f kube/local/minikube/config.yaml
	kubectl apply -f kube/local/minikube/deployment.yaml

build-local-dev:
	docker build -f kube/local/minikube/Dockerfile -t danibachar/app:latest ..
	docker push danibachar/app:latest

run-local-dev: build-local-dev
	docker run --env-file ./kube/local/docker/env.list -p 80:8081 app:local
