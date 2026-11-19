# 04. LAN 開発サーバー構築手順書（Ubuntu 24.04 + 2台 Mac リモート開発）

- **対象マシン**: Ubuntu 24.04.5 LTS（12 vCPU / 46 GB RAM / LAN IP: `192.168.0.253`）
- **ネットワーク方針**: **自宅 LAN 限定アクセス**（外網ポート開放なし）
- **担当**: メンバー A（Infra / Platform 担当）

---

## 1. 構成イメージ（2 台の Mac → 共有 Linux 開発サーバー）

- **共有インフラ（1 セットのみ起動）**：この Linux 上の Docker Compose で `postgres` / `minio` / `mlflow` / `prometheus` / `grafana` を常駐させる。
- **コード作業ディレクトリ（必ず分離）**：メンバー A・メンバー B で Linux ユーザーを分け、それぞれ自分のホーム配下に `git clone` して開発する（**同一ディレクトリで共同編集しないこと！**）。

| サービス | ポート | Mac ブラウザからのアクセス（LAN 直結） |
| :--- | :---: | :--- |
| Target App (`order-service`) | `8001` | `http://192.168.0.253:8001/docs` |
| Inference API | `8002` | `http://192.168.0.253:8002/docs` |
| MLflow Tracking UI (Sprint 1) | `5000` | `http://192.168.0.253:5000` |
| MinIO S3 API / Console (Sprint 1) | `9000` / `9001` | `http://192.168.0.253:9001` |
| Prometheus | `9090` | `http://192.168.0.253:9090` |
| Grafana (Sprint 3) | `3000` | `http://192.168.0.253:3000` |

> **ルーター設定の推奨**：自宅ルーターの管理画面で、この Linux マシンの MAC アドレスに `192.168.0.253` を **DHCP 固定割り当て** しておくと、再起動しても IP が変わらず快適です。

---

## 2. Step 1：OpenSSH Server の有効化（Linux 側）

Linux のターミナルで実行してください：

```bash
sudo apt-get update
sudo apt-get install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh --no-pager
```

### LAN 限定ファイアウォール（任意・推奨）
```bash
# 自宅 LAN (192.168.0.0/24) からのみ SSH および開発ポートを許可
sudo ufw allow from 192.168.0.0/24 to any port 22 proto tcp
sudo ufw allow from 192.168.0.0/24 to any port 3000,5000,8001,8002,9000,9001,9090 proto tcp
sudo ufw status
# 問題なければ有効化: sudo ufw enable
```

---

## 3. Step 2：Docker Engine + Docker Compose の導入（Ubuntu 24.04 公式）

```bash
# 1. 前提パッケージ導入と Docker 公式 GPG キー登録
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 2. APT リポジトリ追加
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 3. Docker Engine + Compose プラグインをインストール
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. sudo なしで docker を使えるようにグループ追加
sudo usermod -aG docker "$USER"
```

**反映確認**（一度ログアウト＆再ログイン、または `newgrp docker` 実行後）：
```bash
docker --version
docker compose version
docker run --rm hello-world
```

---

## 4. Step 3：メンバー B 用 Linux アカウント作成（環境分離）

2 人の Git 署名・SSH 鍵・作業ブランチが混ざらないよう、メンバー B（`xinchen`）用に独立アカウントを作ります：

```bash
# ユーザー作成（パスワードを設定）
sudo adduser xinchen

# docker 操作を許可（必要なら sudo も追加可）
sudo usermod -aG docker xinchen
```

各メンバーは自分のホームディレクトリで Git 初期設定を行います：
```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
git config --global init.defaultBranch main
```

---

## 5. Step 4：2 台の Mac からの SSH 接続設定

### Mac 側で SSH 鍵作成＆コピー（メンバー A・B それぞれの Mac で実行）
```bash
# 鍵がなければ作成
ssh-keygen -t ed25519 -C "mac-opspulse"

# メンバー A の Mac
ssh-copy-id jintao@192.168.0.253

# メンバー B の Mac
ssh-copy-id xinchen@192.168.0.253
```

### Mac 側 `~/.ssh/config` の設定例
```sshconfig
Host opspulse-dev
  HostName 192.168.0.253
  User jintao          # メンバー B の Mac では xinchen に変更
  IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 60
```

設定後、Mac から以下で接続できれば完了です：
```bash
ssh opspulse-dev
```
あとは **VS Code / Antigravity の Remote-SSH** で `opspulse-dev` を開くだけで、ローカルと同じ感覚で快適に開発できます。

---

## 6. 完了確認チェックリスト（メンバー A）
- [ ] `systemctl is-active ssh` が `active`
- [ ] `docker compose version` が動作し、`make up` で v0.1 の 3 コンテナ（`target-app`, `inference-api`, `prometheus`）が起動する
- [ ] Mac A / Mac B の両方から `ssh opspulse-dev` でパスワードなし接続できる
- [ ] Mac のブラウザから `http://192.168.0.253:8001/docs` と `http://192.168.0.253:9090` が開く
