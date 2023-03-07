
        function toggleDetails(id)
    {
            var element = document.getElementById("details-" + id);
            if (element.style.display === "none") {
                element.style.display = "block";
            } else {
                element.style.display = "none";
            }
        }
