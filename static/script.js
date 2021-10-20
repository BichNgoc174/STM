$(function() {
    $('.sub-folder-tree li').click(function(evt) {
        evt.stopPropagation();
        $(this).toggleClass('expanded');
    });
});