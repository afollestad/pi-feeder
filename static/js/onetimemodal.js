$('.datepicker').pickadate({
    selectMonths: true,
    selectYears: 15,
    container: 'body'
});

$('.timepicker').pickatime({
    autoclose: false,
    twelvehour: true,
    container: 'body'
});

$('#modal-submit').click(function(e) {
    e.preventDefault();
    var date = $('#date').val();
    var time = $('#time').val();

    if (!date || date.trim().length === 0) {
        $('#modal').load('/add_onetime_occurrence/' + escape('Please select a date.'));
        return;
    }
    if (!time || time.trim().length === 0) {
        $('#modal').load('/add_onetime_occurrence/' + escape('Please select a time.'));
        return;
    }

    var dateTime = moment(date + ' ' + time).toDate();
    var data = {
        year: dateTime.getFullYear(),
        month: dateTime.getMonth() + 1,
        day: dateTime.getDate(),
        hour: dateTime.getHours(),
        minute: dateTime.getMinutes()
    };

    var btn = $(this);
    btn.attr('disabled', 'disabled');
    post('/add_onetime_occurrence', data, function(response, error) {
        if (error) {
            btn.removeAttr('disabled');
            window.location.href = '/add_onetime_occurrence/' + escape(error);
            return;
        }
        refresh();
        $('#modal').modal('close');
    });
});