var clipboardContent = document.getElementById("clipboard-content");

const API_PREFIX = "/api/v1";

function callRawApi(url, json, completionHandler) {
    fetch(API_PREFIX + url, {
        "method": "post",
        "headers": { "content-type": "application/json" },
        "body": JSON.stringify(json)
    }).catch(reason => {
        console.error(reason);
    }).then(response => {
        response.json().then(json => {
            completionHandler(json) 
        })
    });
}

function api(url, json, completionHandler) {
    if (!json["user_id"]) json["user_id"] = user_id;
    if (!json["auth_token"]) json["auth_token"] = auth_token;
    callRawApi(url, json, completionHandler);
}

function getCookieValue(key) {
    return document.cookie.split("; ").find(row => row.startsWith(key + "="))?.split("=")[1];
}

var user_id = getCookieValue("user_id");
var auth_token = getCookieValue("auth_token");

function setAlert(msg, cls = "danger") {
    document.getElementById("msg").innerHTML = `<div class="alert alert-${cls} alert-dismissible fade show" role="alert">
    ${msg}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
}

function deleteClipboardContent(id) {
    api("/clipboard/delete", {
        "clip_id": id
    }, (json) => {
        if (json["deleted"]) {
            document.getElementById("clip-" + json["clip_id"]).remove();
            if (clipboardContent.innerHTML.trim().length == 0) {
                clipboardContent.innerHTML = "<p>Clipboard is empty.</p>";
            }
        }
    });
}

function appendClipboardContent(json) {
    var card = document.createElement("div");
    card.id = "clip-" + json["clip_id"];
    card.className = "card mb-3";

    var delBtn = document.createElement("button");
    delBtn.className = "btn-close position-absolute top-0 end-0 p-2";
    delBtn.addEventListener("click", () => { deleteClipboardContent(json["clip_id"]) });
    card.appendChild(delBtn);

    var outerRow = document.createElement("div");
    outerRow.className = "row g-0";

    if (json["clip_image"]) {
        var imageColumn = document.createElement("div");
        imageColumn.className = "col-md-2";
        var imgHtml = `<img src="${json["clip_image"]}" class="img-fluid rounded-start">`;
        if (json["clip_url"]) {
            imageColumn.innerHTML = `<a target="_new" href="${json["clip_url"]}">${imgHtml}</a>`;
        } else {
            imageColumn.innerHTML = imgHtml;
        }
        outerRow.appendChild(imageColumn);
    }

    var bodyColumn = document.createElement("div");
    bodyColumn.className = json["clip_image"] ? "col-md-10" : "col-md-12";
    
    var cardBody = document.createElement("div");
    cardBody.className = "card-body";

    var titleText = json["clip_title"] ? json["clip_title"] : json["clip_url"] ? json["clip_url"].substring(0, 120) : "";
    if (titleText) {
        var titleHtml = json["clip_url"] ? `<a target="_new" href="${json["clip_url"]}">${titleText}</a>` : titleText;
        var cardTitle = document.createElement("div");
        cardTitle.className = "card-title";
        cardTitle.innerHTML = `<h5 class="card-title">${titleHtml}</h5>`;
        cardBody.appendChild(cardTitle);
    }

    if (json["clip_description"]) {
        var cardText = document.createElement("div");
        cardText.className = "card-text";
        cardText.innerHTML = json["clip_description"];
        cardBody.appendChild(cardText);
    }

    var cardText = document.createElement("div");
    cardText.className = "card-text position-absolute bottom-0 end-0 p-2";
    cardText.innerHTML = `<small class="text-body-secondary">${json["clip_time"]}</small>`;
    cardBody.appendChild(cardText);

    bodyColumn.appendChild(cardBody);

    outerRow.appendChild(bodyColumn);
    card.appendChild(outerRow);
    clipboardContent.prepend(card);
}

function doFormLogin(signUp = false) {
    var userId = document.getElementsByName("user_id")[0];
    var userPassword = document.getElementsByName("user_password")[0];
    var userMail = document.getElementsByName("user_mail")[0];

    if (!signUp) {
        callRawApi("/auth/login", {
            "user_id": userId.value,
            "user_password": userPassword.value
        }, (json) => {
            if (json["error"]) {
                setAlert(json["error"]);
            } else {
                document.cookie = "auth_token=" + json["auth_token"] + "; Max-Age=31536000; SameSite=Lax; Secure";
                document.cookie = "user_id=" + json["user_id"] + "; Max-Age=315360000; SameSite=Lax; Secure";
                self.location.href = "/";
            }
        });
    } else {
        callRawApi("/auth/signup", {
            "user_id": userId.value,
            "user_password": userPassword.value,
            "user_mail": userMail.value
        }, (json) => {
            if (json["error"]) {
                setAlert(json["error"]);
            } else {
                setAlert("Signed up! You can login now.", "success");
            }
        });
    }
}

function togglePrivacy(makePublic) {
    api("/user/privacy", {
        "privacy": (makePublic ? "public" : "private")
    }, (json) => {
        if (json["privacy"] == "private") {
            document.getElementById("btnMakePrivate")?.classList.add("d-none");
            document.getElementById("btnMakePublic")?.classList.remove("d-none");
            setAlert(`Your clipboard is private now. Only you can see your links.`, "warning");
        } else if (json["privacy"] == "public") {
            url = self.location.protocol + "//" + self.location.host + "/u/" + user_id;
            setAlert(`Your clipboard is public now. Everyone can see your links at <a target="_new" href=\"${url}\">${url}</a>`, "warning");
            document.getElementById("btnMakePublic")?.classList.add("d-none");
            document.getElementById("btnMakePrivate")?.classList.remove("d-none");
        }
    });
}

window.addEventListener("load", () => {
    document.forms["login"]?.addEventListener("submit", (event) => {
        event.preventDefault();
        doFormLogin(false);
    });

    document.forms["signup"]?.addEventListener("submit", (event) => {
        event.preventDefault();
        doFormLogin(true);
    });

    document.getElementById("btnLogout")?.addEventListener("click", () => {
        api("/auth/logout", {}, (json) => {
            if (json["logged_out"]) {
                setAlert("Logged out successfully!", "success");
            } else {
                setAlert("Logged out!", "warning");
            }
            document.cookie = "user_id=; Max-Age=0;";
            document.cookie = "auth_token=; Max-Age=0;"
            setTimeout(() => { self.location.href = "/"; }, 2000);
        });
    });

    document.getElementById("btnMakePublic")?.addEventListener("click", () => { togglePrivacy(true); });
    document.getElementById("btnMakePrivate")?.addEventListener("click", () => { togglePrivacy(false); });

    document.getElementById("btnAddClip")?.addEventListener("click", () => {
        var inputData = document.getElementById("inputData");
        api("/clipboard/add", {
            "clip_data": inputData.value
        }, (json) => {
            if (json["error"]) {
                setAlert(json["error"]);
            } else {
                inputData.value = "";
                if (clipboardContent.innerHTML == "<p>Clipboard is empty.</p>") {
                    clipboardContent.innerHTML = "";
                }
                appendClipboardContent(json);
            }
        });
    });

    document.getElementById("inputData")?.addEventListener("keyup", event => {
        if (event.key == "Enter") {
            document.getElementById("btnAddClip").click();
        }
    });

    if (user_id) {
        if (!self.location.pathname.startsWith("/u/")) {
            api("/clipboard/list", {}, (json) => {
                if (json["count"] == 0) {
                    clipboardContent.innerHTML = "<p>Clipboard is empty.</p>"
                } else {
                    json["list"].forEach(item => appendClipboardContent(item));
                }
            });
        } else {
            var show_user = self.location.pathname.split('/').pop();
            api("/clipboard/list", {
                "user_id": show_user
            }, (json) => {
                if (json["count"] == 0) {
                    clipboardContent.innerHTML = "<p>Clipboard is empty.</p>"
                } else {
                    clipboardContent.innerHTML = "";
                    json["list"].forEach(item => appendClipboardContent(item));
                }
            });
        } 
    }
});