$(document).ready(function () {
    $("#id_avatar").change(function () {
        const chosen_file = $(this).prop("files")[0];
        $("#image_preview").prop("src", URL.createObjectURL(chosen_file));
    })

})

