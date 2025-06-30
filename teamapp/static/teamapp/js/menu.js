// サイドメニューの表示切替
document.getElementById('sideMenuToggle').addEventListener('click', function() {
    const sideMenu = new bootstrap.Offcanvas(document.getElementById('sideMenu'));
    sideMenu.toggle();
});
