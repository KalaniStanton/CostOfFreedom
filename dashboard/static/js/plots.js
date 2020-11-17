$('#first_cat').on('change',function(){
    console.log("test");
    $.ajax({
        url: "/bar",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('first_cat').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data );
        }
    });
})
