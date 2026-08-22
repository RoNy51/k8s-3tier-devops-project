pipeline {
    agent { label 'docker' }

    environment {
        AWS_ACCOUNT_ID = "471597061700"
        AWS_REGION     = "eu-west-1"
        ECR_REPO       = "3tier-app"
        ECR_URI        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Source') {
            steps {
                checkout scm
                sh 'git rev-parse --short HEAD > .git-commit'
                script {
                    env.GIT_COMMIT_SHORT = readFile('.git-commit').trim()
                }
                echo "Checked out commit ${env.GIT_COMMIT_SHORT}, build #${env.BUILD_NUMBER}"
            }
        }

        stage('Build') {
            steps {
                sh "docker build -t ${ECR_REPO}:${IMAGE_TAG} ."
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker network create ci-test-net || true
                    docker run -d --rm --name ci-postgres \
                        --network ci-test-net \
                        -e POSTGRES_USER=appuser \
                        -e POSTGRES_PASSWORD=apppassword \
                        -e POSTGRES_DB=appdb \
                        postgres:16
                    sleep 8
                '''
                sh """
                    docker run --rm \
                        --network ci-test-net \
                        -e DB_HOST=ci-postgres \
                        -e DB_PORT=5432 \
                        -e DB_NAME=appdb \
                        -e DB_USER=appuser \
                        -e DB_PASSWORD=apppassword \
                        --entrypoint sh \
                        ${ECR_REPO}:${IMAGE_TAG} \
                        -c "pip install --no-cache-dir -r app/requirements-test.txt && pytest app/test_main.py -v"
                """
            }
            post {
                always {
                    sh 'docker stop ci-postgres || true'
                    sh 'docker network rm ci-test-net || true'
                }
            }
        }

        stage('Release') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'aws-ecr-creds',
                    usernameVariable: 'AWS_ACCESS_KEY_ID',
                    passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                )]) {
                    sh '''
                        aws ecr get-login-password --region $AWS_REGION | \
                            docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                    '''
                    sh "docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}"
                    sh "docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URI}:latest"
                    sh "docker push ${ECR_URI}:${IMAGE_TAG}"
                    sh "docker push ${ECR_URI}:latest"
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Image pushed: ${ECR_URI}:${IMAGE_TAG}"
                echo "Deploy stage placeholder — ArgoCD sync wiring comes next session"
            }
        }
    }

    post {
        always {
            sh "docker rmi ${ECR_REPO}:${IMAGE_TAG} || true"
        }
        success {
            echo "Pipeline succeeded for build #${env.BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline failed — check stage logs above"
        }
    }
}
