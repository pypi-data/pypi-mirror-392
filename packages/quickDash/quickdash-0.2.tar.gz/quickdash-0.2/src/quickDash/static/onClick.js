const sideBar = document.getElementById("sideBar");
function sideBarResize()
{
    if (sideBar.style.width == "12vw")
    {
        sideBar.style.fontSize = "10px";
    }
    else
    {
        sideBar.style.fontSize = "0";
    }
}
