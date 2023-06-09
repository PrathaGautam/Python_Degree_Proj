

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
async function deleteAd(ad_id)
{
    let response = await fetch('/delete_ad/' + ad_id,
        {
            method: 'POST',
        });
    if (response.redirected) {
    window.location.href = '/products';
  }

}

function editAd(ad_id)
{
    console.log("edit ad function.")
    let response = fetch('/editablepage/' + ad_id,
        {
            method: 'GET',
        });

}
function editAd(ad_id)
{
    console.log("edit ad function.")
    window.location.href = '/editablepage/' + ad_id;
}

function updateChanges(ad_id)
{
    const formData = new FormData(document.getElementById("update_changes_form"));

   //sending put request to server with updated data
    fetch(`/editablepage/${ad_id}`,
        {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if(response.redirected)
            {
                window.location.href = response.url;
            } else {
                console.error('Failed to update ad:', response.statusText);
            }
        })
        .catch(error => console.error('Error:',error));
}


const buttons = document.querySelectorAll('.active');

buttons.forEach((button) => {
  button.addEventListener('click', () => {
    buttons.forEach((button) => {
      button.classList.remove('active');
    });
    button.classList.add('active');
  });
});










