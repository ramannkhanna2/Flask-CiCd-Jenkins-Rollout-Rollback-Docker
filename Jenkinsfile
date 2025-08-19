pipeline {
    agent any

    environment {
        APP_NAME = "raman-flask-app"
        VERSION = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('Build Docker Image') {
            steps {
                sh 'sudo docker build -t $APP_NAME:$VERSION .'
            }
        }

        stage('Deploy to Staging') {
            steps {
                sh '''
                sudo docker rm -f ${APP_NAME}-staging || true
                sudo docker run -d --name ${APP_NAME}-staging -p 5001:5000 $APP_NAME:$VERSION
                echo "Staging running at port 5001/"
                '''
            }
        }

        stage('Approval for Production') {
            steps {
                input message: "Promote this version to Production?"
            }
        }

        stage('Deploy to Production') {
            steps {
                script {
                    try {
                        sh '''
                        # Stop old prod container but keep image
                        sudo docker rm -f ${APP_NAME}-prod || true

                        # Run new version
                        sudo docker run -d --name ${APP_NAME}-prod -p 5002:5000 $APP_NAME:$VERSION

                        # If successful, mark this as the stable 'latest'
                        sudo docker tag $APP_NAME:$VERSION $APP_NAME:latest
                        echo "Production running at port 5002/"
                        '''
                    } catch (err) {
                        error("Production deployment failed!")
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "⚠️ Deployment failed! Rolling back to last stable version..."
            sh '''
            sudo docker rm -f ${APP_NAME}-prod || true
            sudo docker run -d --name ${APP_NAME}-prod -p 5002:5000 $APP_NAME:latest
            '''
        }
    }
}
