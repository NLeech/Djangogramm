function changeSelectedImagePreview(event){
    const chosen_file = $(this).prop("files")[0];
    const imageURL =  URL.createObjectURL(chosen_file);
    const imagePreview = $(`<img src='${imageURL}'  alt="preview" height=100> `)
    $(this).parent().after(imagePreview);
}

function cloneHiddenImageForm(event) {
    const formRegex = RegExp(`images-(\\d){1}-`, 'g');
    const imagesFormQty = Number($("#id_images-TOTAL_FORMS").val());
    $("#id_images-TOTAL_FORMS").val(imagesFormQty + 1);

    const newImageForm = $("#hidden_image_form").clone(true);

    // set new id and make visible cloned form (see forms.css)
    newImageForm.prop("id", "image_form-" + imagesFormQty);

    // set new tags for the all new form elements
    const newHTML = newImageForm.html().replace(formRegex, `images-${imagesFormQty}-`);
    newImageForm.html(newHTML);

    $("#add-image-form").before(newImageForm);
    $(`#id_images-${imagesFormQty}-image`).on("change", changeSelectedImagePreview);
}

$(document).ready(function () {
    $("#add-image-form").click(cloneHiddenImageForm);
})