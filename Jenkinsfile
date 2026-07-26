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

        stage('Prepare Build Info') {
            steps {
                script {
                    env.GIT_SHA = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Building Git commit: ${env.GIT_SHA}"
                    echo "Image: ${IMAGE}:${env.GIT_SHA}"
                    echo "Latest: ${IMAGE}:latest"
                }
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
                sh '''
                    docker build \
                        -t ${IMAGE}:${GIT_SHA} \
                        -t ${IMAGE}:latest \
                        .
                '''
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
                        credentialsId: 'AWS-user',
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
                        credentialsId: 'AWS-user',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {
                    sh '''
                        echo "Pushing commit image..."
                        docker push ${IMAGE}:${GIT_SHA}

                        echo "Pushing latest image..."
                        docker push ${IMAGE}:latest
                    '''
                }
            }
        }

        stage('Verify ECR Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'AWS-user',
                        usernameVariable: 'AWS_ACCESS_KEY_ID',
                        passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {
                    sh '''
                        aws ecr describe-images \
                            --repository-name ${ECR_REPO} \
                            --region ${AWS_REGION} \
                            --image-ids imageTag=latest
                    '''
                }
            }
        }
        stage('Deploy to ECS') {
    steps {

        withCredentials([
            usernamePassword(
                credentialsId: 'AWS-user',
                usernameVariable: 'AWS_ACCESS_KEY_ID',
                passwordVariable: 'AWS_SECRET_ACCESS_KEY'
            )
        ]) {

            sh '''
                echo "Starting DeployGuard Blue/Green deployment..."

                aws ecs update-service \
                    --cluster deployguard-cluster \
                    --service deployguard-task-service-fcszavcr \
                    --force-new-deployment \
                    --region ap-south-1

                echo "ECS deployment started!"
            '''
        }
    }
}
    }

    post {

        success {
            echo 'DeployGuard CI pipeline successful!'
            echo "Image: ${IMAGE}:${GIT_SHA}"
            echo "Latest: ${IMAGE}:latest"
        }

        failure {
            echo 'DeployGuard CI pipeline failed!'
        }

    }
}
