# PipelineGen

**Interactive DevSecOps CI/CD Pipeline Generator**

PipelineGen is a command-line tool that automatically generates **secure, production-ready DevSecOps pipelines** for GitHub Actions.
It asks simple interactive questions and produces a fully optimized pipeline with:

* OIDC authentication
* SAST, SCA, secret scanning
* Docker multi-arch builds
* Coverage reports
* SonarQube integration
* Deployment workflows
* Professional comments + formatted YAML

No YAML knowledge required — just answer the prompts and your pipeline is ready.

---

## ✨ Features

### 🔧 Technology Support

✔ Java (Maven / Gradle)
✔ Python
✔ Node.js
✔ Go (coming soon)
✔ .NET (coming soon)

### 🔒 Security Built-in

* SpotBugs / Bandit (SAST)
* Trivy filesystem & image scanning
* Gitleaks secret detection
* SARIF reports
* OIDC authentication for AWS

### 🐳 Containerization

* Docker build
* Buildx
* Multi-architecture images
* ECR login (via OIDC)
* Layer caching for faster builds

### 🧪 Testing & Coverage

* JUnit / PyTest / Jest support
* Auto-generated test artifacts
* Code coverage upload
* Compatible with SonarQube

### 🚀 Deployment

* AWS ECS
* AWS EKS
* Lambda
* Kubernetes
* Or no deployment (if not needed)

---

## 📦 Installation

Install from PyPI:

```
pip install simpledevsecops
```

---

## ▶️ Usage

Run the generator:

```
simpledevsecops
```

Follow the interactive prompts:

* Choose language
* Select build tool
* Enable/disable security scans
* Choose deployment target
* Enable caching / concurrency
* Set job timeouts
* Choose filename

After answering, your pipeline is generated inside:

```
generated-pipelines/<your-pipeline-name>.yaml
```

---

## 📁 Example Output

```
generated-pipelines/
└── java-devsecops-pipeline.yaml
```

The file includes:

* Step-by-step comments
* Security markers
* Optimized job ordering
* Ready-to-run GitHub Actions pipeline

---

## 🔐 Required Secrets (Based on your choices)

* AWS_ROLE_ARN
* AWS_ACCOUNT_ID
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* SONAR_TOKEN

Automatically detected and shown after generation.

---

## ⚙️ Why Use PipelineGen?

* No need to manually create YAML files
* Ensures best practices for DevSecOps
* Generates pipelines with consistent structure
* Supports multiple languages
* Saves hours of configuration work
* Perfect for both beginners and senior engineers

---

## 🤝 Contributing

Pull requests and feature requests are welcome!
Feel free to open issues if you want new features like:

* Terraform CI integration
* Azure DevOps support
* GitLab CI support
* Template packs

---

## 🧑‍💻 Author

**Sourav Kumar**
Email: [1109souravkumar@gmail.com](mailto:1109souravkumar@gmail.com)
