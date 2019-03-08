init:
	minikube start --extra-config=controller-manager.horizontal-pod-autoscaler-use-rest-clients=true --extra-config=controller-manager.horizontal-pod-autoscaler-sync-period=5s --extra-config=controller-manager.horizontal-pod-autoscaler-downscale-stabilization=1m0s --v=5
	eval $(minikube docker-env)
	minikube addons enable metrics-server

init-and-deploy:
	init-minikube
	deploy-local

cleanup:
	delete-deploy
	minikube stop

deploy:
	kubectl apply -f hpa.yaml

delete-deploy:
	kubectl delete -f hpa.yaml