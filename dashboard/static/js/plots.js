var firstVariable = "";
var secondVariable = "";

$( document ).ready(function() {
    populateSelect($("#first_cat_only"));
    populateSelect($("#first_cat"));
    populateSelect($("#second_cat"));

    $('#first_cat_only').on('change',function(){
        firstVariable = $('#first_cat_only').val();
        text = $( "#first_cat_only option:selected" ).text();
        $("#loading").show();
        $("#bargraph").hide();
        $("#title").html();
        $.ajax({
            url: "/data/scatter_only",
            type: "GET",
            contentType: 'application/json;charset=UTF-8',
            data: {
                'firstVariable': firstVariable
            },
            dataType:"json",
            success: function (data) {
                $("#loading").hide();
                $("#bargraph").show();
                $("#title").html(text);
                Plotly.newPlot('bargraph', data );
            }
        });
    });

    $('#first_cat').on('change',function(){
        firstVariable= $('#first_cat').val();
        if(firstVariable != "" && secondVariable != "") updateVariables();
    });

    $('#second_cat').on('change',function(){
        secondVariable= $('#second_cat').val();
        if(firstVariable != "" && secondVariable != "") updateVariables();
    });
});

const populateSelect = (targetDiv) => {
    $.each(HFI_Dictionary,function(key, value) 
    {
        if(typeof HFI_Dictionary[key] === 'object') {
        targetDiv.append('<option value="' + key + '" disabled>' + key + '</option>');
             $.each(HFI_Dictionary[key],function(key2, value2) 
            {
                if(typeof HFI_Dictionary[key][key2] === 'object') {
                targetDiv.append('<option value="' + key2 + '" disabled> -- ' + key2 + '</option>');
                $.each(HFI_Dictionary[key][key2],function(key3, value3)
                {       
                               
                    targetDiv.append('<option value="' + value3 + '"> ---- ' + key3 + '</option>');
                });
                } else {
                targetDiv.append('<option value="' + value2 + '">' + key2 + '</option>');
                }
            });
        } else {
        targetDiv.append('<option value="' + value + '">' + key + '</option>');    
        }
    });
}


const updateVariables = () => {
    console.log("update variables");
    $("#loading").show();
    $("#bargraph").hide();
    text = $( "#first_cat_only option:selected" ).text();
    $("#title").html();
    $.ajax({
        url: "/data/scatter",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'firstVariable': firstVariable,
            'secondVariable': secondVariable,
        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data );
            $("#loading").hide();
            $("#title").html(text);
            $("#bargraph").show();
        }
    });
}