$(document).ready(function() {
    $('#countrySelect').change(function() {
        var country = $(this).val();
        $.post('/cities', {country: country}, function(data) {
            $('#citySelect').empty();
            $('#citySelect').append('<option value="">Select a City</option>');
            $.each(data, function(i, city) {
                $('#citySelect').append('<option value="' + city + '">' + city + '</option>');
            });
        });
    });
});
