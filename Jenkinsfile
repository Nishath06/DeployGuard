pipeline {

    agent any

    environment {
        AWS_REGION = 'ap-south-1'

        AWS_ACCOUNT_ID = '177001539059'

        ECR_REPO = 'deployguard'

        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

        IMAGE = "${ECR_REGISTRY}/${ECR_REPO}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt

                    pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                script {

                    env.GIT_SHA = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    sh """
                        docker build \
                        -t ${IMAGE}:${GIT_SHA} \
                        .
                    """
                }
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                    trivy image \
                    --severity HIGH,CRITICAL \
                    --exit-code 0 \
                    ${IMAGE}:${GIT_SHA}
                '''
            }
        }

        stage('ECR Login') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    sh '''
                        aws ecr get-login-password \
                        --region ${AWS_REGION} \
                        | docker login \
                        --username AWS \
                        --password-stdin ${ECR_REGISTRY}
                    '''
                }
            }
        }

        stage('Push ECR') {
            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-credentials',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    sh '''
                        docker push ${IMAGE}:${GIT_SHA}
                    '''
                }
            }
        }

    }

    post {

        success {
            echo 'DeployGuard CI pipeline successful!'
        }

        failure {
            echo 'DeployGuard CI pipeline failed!'
        }

    }

}