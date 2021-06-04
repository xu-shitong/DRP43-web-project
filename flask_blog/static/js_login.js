$(function() {
    $("p#login").click(function() {
        $.getJSON('login', {
            username: $('input[name="username"]').val(),
            password: $('input[name="password"]').val()
        }, function(data) {
            alert(data.result)
        });
        return false;
    })
})
