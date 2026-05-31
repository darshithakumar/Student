pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'darshithakumar'
        BACKEND_IMAGE   = "${DOCKER_HUB_USER}/college-backend"
        FRONTEND_IMAGE  = "${DOCKER_HUB_USER}/college-frontend"
        IMAGE_TAG       = "${BUILD_NUMBER}"
        DOCKER_CREDS    = credentials('dockerhub-creds')
    }

    stages {

        // ── 1. CHECKOUT ────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Cloning repository from GitHub...'
                checkout scm
            }
        }

        // ── 2. BUILD DOCKER IMAGES ─────────────────────────────────────
        stage('Build Docker Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        echo '🐳 Building Backend Docker image...'
                        bat "docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} -t ${BACKEND_IMAGE}:latest ./Backend"
                    }
                }
                stage('Build Frontend') {
                    steps {
                        echo '🐳 Building Frontend Docker image...'
                        bat "docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} -t ${FRONTEND_IMAGE}:latest ./Frontend"
                    }
                }
            }
        }

        // ── 3. PUSH TO DOCKER HUB ──────────────────────────────────────
        stage('Push to Docker Hub') {
            steps {
                echo '📤 Logging in to Docker Hub and pushing images...'
                bat "docker login -u %DOCKER_CREDS_USR% -p %DOCKER_CREDS_PSW%"

                bat "docker push ${BACKEND_IMAGE}:${IMAGE_TAG}"
                bat "docker push ${BACKEND_IMAGE}:latest"

                bat "docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                bat "docker push ${FRONTEND_IMAGE}:latest"
            }
        }

        // ── 4. DEPLOY TO KUBERNETES ────────────────────────────────────
        stage('Deploy to Kubernetes') {
            steps {
                echo '☸️  Deploying updated images to Kubernetes cluster...'

                // Update image tags in-place so the correct build is rolled out
                bat "kubectl set image deployment/backend-deployment  backend=${BACKEND_IMAGE}:${IMAGE_TAG}  --record"
                bat "kubectl set image deployment/frontend-deployment frontend=${FRONTEND_IMAGE}:${IMAGE_TAG} --record"

                // Apply any manifest changes (new config maps, services, etc.)
                bat "kubectl apply -f k8s/"

                // Wait for rollouts to finish (timeout 3 minutes each)
                bat "kubectl rollout status deployment/backend-deployment  --timeout=180s"
                bat "kubectl rollout status deployment/frontend-deployment --timeout=180s"
            }
        }

        // ── 5. VERIFY DEPLOYMENT ───────────────────────────────────────
        stage('Verify Deployment') {
            steps {
                echo '✅ Verifying running pods and services...'
                bat "kubectl get pods -o wide"
                bat "kubectl get svc"
                bat "kubectl get deployments"
            }
        }
    }

    // ── POST ACTIONS ───────────────────────────────────────────────────
    post {
        success {
            echo """
╔══════════════════════════════════════════════════╗
║  ✅  Pipeline completed SUCCESSFULLY!            ║
║  Backend  : ${BACKEND_IMAGE}:${IMAGE_TAG}        ║
║  Frontend : ${FRONTEND_IMAGE}:${IMAGE_TAG}       ║
╚══════════════════════════════════════════════════╝
"""
        }
        failure {
            echo """
╔══════════════════════════════════════════════════╗
║  ❌  Pipeline FAILED. Check the logs above.      ║
╚══════════════════════════════════════════════════╝
"""
        }
        always {
            echo '🧹 Cleaning up dangling Docker images...'
            bat "docker image prune -f"
        }
    }
}