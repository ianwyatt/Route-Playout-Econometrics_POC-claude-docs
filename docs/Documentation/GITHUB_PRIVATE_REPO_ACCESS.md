# GitHub Private Repository Access

How to clone the private RouteResearch repository using fine-grained personal access tokens.

---

## Fine-Grained Token Setup

GitHub recommends fine-grained tokens over classic tokens for better security.

### 1. Create Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens**
2. Click **Generate new token**
3. Set token name and expiration
4. Under **Resource owner**, select **RouteResearch** (the organisation)
5. Under **Repository access**, select **All repositories** or the specific repo

### 2. Set Permissions

Under **Repository permissions**, enable:

| Permission | Access Level |
|------------|--------------|
| **Contents** | Read-only |
| **Metadata** | Read-only (auto-selected) |

### 3. Generate and Copy

Click **Generate token** and **copy the token value immediately** — it won't be shown again.

The token starts with `github_pat_` (not `ghp_` like classic tokens).

---

## Clone Command

Use `x-access-token` as the username (not your GitHub username):

```bash
git clone https://x-access-token:github_pat_YOUR_TOKEN_HERE@github.com/RouteResearch/Route-Playout-Econometrics_POC.git
```

Replace `github_pat_YOUR_TOKEN_HERE` with your actual token value.

---

## Organisation Approval

If the RouteResearch org requires token approval:

1. After creating the token, it may show as "Pending" in the org
2. An org admin must approve it at: RouteResearch → Settings → Personal access tokens → Pending requests
3. Once approved, the token appears under "Active tokens"

---

## Troubleshooting

### "Invalid username or token" error

- Ensure you're using `x-access-token` as the username, not your GitHub username
- Ensure the token value starts with `github_pat_`
- Check the token has **Contents: Read** permission
- Verify the token is approved in the org's active tokens list

### Token not working after creation

You need to **regenerate** the token to see its value again. The value is only shown once when created.

---

## Alternative: PyCharm OAuth

PyCharm can authenticate via browser without manual token creation:

1. PyCharm → **Get from VCS** → **GitHub** → **Log in via GitHub**
2. Browser opens, authorize PyCharm
3. Clone from the repository list

---

*Last Updated: 5 February 2026*
