# AWS Infrastructure as Code (`infra/terraform/`)

- **Owner**: メンバー A（Platform / Infra 担当）
- **対象 Issue**: Sprint 3, **Issue #13**
- **コスト最適化設計方針（重要）**:
  - 個人検証フェーズでの月額コストを **\$20 以下** に抑えるため、**NAT Gateway（月額約\$32）は作成しない**。
  - パブリックサブネット + 厳格な Security Group（必要ポートのみ許可）上に ECS Fargate（Spot 可）を配置する。
  - 管理対象リソース：S3（データ＆MLflow Artifact）、ECR、IAM（最小権限タスク実行ロール）、ECS Cluster/Service、CloudWatch Logs。
  - 演習終了後は必ず `terraform destroy`（`make aws-down`）で課金停止できるようにする。
