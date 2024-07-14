function setusertoken(token) {
  localStorage.setItem("usertoken", token);
}

function getusertoken() {
  let token = localStorage.getItem("usertoken");
  return { token: token };
}

function setemailtoken(token) {
  localStorage.setItem("emailtoken", token);
}

function getemailtoken() {
  let token = localStorage.getItem("emailtoken");
  return { token: token };
}
