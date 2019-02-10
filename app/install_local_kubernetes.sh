#!/bin/bash

#Prerequisits:
#HomeBrew
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
#VirtualBox
brew cask install virtualbox
#Docker
brew install docker
#Kubectl
brew install kubectl
#NOTE - if we want to have all of gcloud cli we should download it from here and install
#https://cloud.google.com/sdk/docs/quickstart-mac-os-x
# install minikube
homebrew cask install minikube
