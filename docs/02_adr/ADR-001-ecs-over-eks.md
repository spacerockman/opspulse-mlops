# ADR-001: クラウド推論基盤として EKS / SageMaker ではなく AWS ECS Fargate を採用する

- **ステータス**: Accepted（承認済）
- **決定日**: 2026-11-19
- **決定者**: Tech Lead / Platform チーム

## コンテキスト（Context）
2 名体制・8 週間の中小規模チームで、日本企業の採用市場でも評価される準本番 MLOps 推論基盤を構築する必要がある。クラウド実行基盤の候補として以下を比較した：
1. Amazon EKS（Kubernetes + Kubeflow）
2. Amazon SageMaker Endpoints
3. Amazon ECS on Fargate + Terraform

## 決定（Decision）
**Amazon ECS on Fargate（Terraform 管理、NAT Gateway なしのコスト最適化構成）** を採用する。

## 理由（Rationale）
- **運用負荷とコストの最適化**：EKS はコントロールプレーンだけで月額 \$73 以上＋ワーカーノード＋複雑なクラスタ運用が必要で、2 名体制の本プロジェクトでは本質の MLOps ライフサイクル実装（評価・ドリフト・ロールバック）に割く時間を奪う。
- **ベンダーロックイン回避と日本市場適性**：FastAPI + Docker + ECR + ECS Fargate + Terraform は日本の SaaS / SIer / 事業会社で最も採用実績が多く、汎用性が高い。
- **ローカルとの一貫性**：Docker コンテナのままローカル（Docker Compose）から ECS へ移行できるため、デバッグと CI/CD 設計が明快になる。

## トレードオフ（Consequences）
- 将来的に大規模 GPU 推論や数十モデルのマルチテナント運用が必要になった場合は、EKS や SageMaker への移行を再検討する。
- コスト抑制のため NAT Gateway を省く構成（パブリックサブネット＋厳格な Security Group）とするが、商用本番ではプライベートサブネット＋VPC Endpoint / NAT Gateway へ拡張する旨を設計書に明記する。
