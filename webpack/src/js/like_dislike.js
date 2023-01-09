function setLikesDislikesNumbers(target, numbersLikeDislikes) {
    $(target).parent().find(".likes-qty").text(numbersLikeDislikes["likes"])
    $(target).parent().find(".dislikes-qty").text(numbersLikeDislikes["dislikes"])
}

function likeOrDislike(event) {
    // get csrf token
    const token = document.cookie.replace(/(?:(?:^|.*;\s*)csrftoken\s*\=\s*([^;]*).*$)|^.*$/, "$1");
    const element = $(this)
    $.ajax({
        url: $(this).attr("data-url"),
        method: "POST",
        headers: {
            "X-CSRFToken": token,
            "Content-Type": "'application/json"
        },
        data: JSON.stringify({action: event.data})

    })
        .done(function (data) {
                setLikesDislikesNumbers(element, data)
        })
}

$(document).ready(function () {
    $(".like").click("like", likeOrDislike);
    $(".dislike").click("dislike", likeOrDislike);
})