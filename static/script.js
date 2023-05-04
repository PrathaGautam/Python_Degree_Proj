

// // Get the button element by its id
// const button = document.getElementById("myButton");
//
// // Disable the button
// button.disabled = true;


//for view details in ad for phone number and email protection :
function toggleDetails(id)
{
    var element = document.getElementById("details-" + id);
    if (element.style.display === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
}

//function for delete ad button :
function deleteAd(ad_id)
{
    let response =  fetch('/delete_ad/' + ad_id,
        {
            method: 'POST',
        });
    if(response.redirected){window.location.href =response.headers.location;}

}


