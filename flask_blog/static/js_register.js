$(function() {
    $("p#register").click(function() {
        $.getJSON('register', {
            username: $('input[name="username"]').val(),
            password: $('input[name="password"]').val()
        }, function(data) {
            alert(data.result)
        });
        return false;
    })
})
