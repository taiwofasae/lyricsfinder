lyrics = [
    {title: 'gospel',content: ''},
    {title: 'dance',content: ''},
    {title: 'classical',content: ''},
    {title: 'example',content: ''}
];

ids = {
    search_phrase: '#searchphrase',
    lyrics_list: 'ul#lyrics-list',
    lyric_title: '#title',
    lyric_content: '#content'
};

lyrics_list = {
    get_template: function () {
        return $(ids.lyrics_list + ' li:first').clone()
    },
    
    reset: function () {
        $(ids.lyrics_list + ' li').html('').addClass('hidden').removeClass('active');
    },
    
    set_data: function (data, index){
        $($(ids.lyrics_list + ' li')[index]).html(data.title).removeClass('hidden');
    },
    
    highlight: function (index){
        $(ids.lyrics_list + ' li').removeClass('active');
        $($(ids.lyrics_list + ' li')[index]).addClass('active')
    },

    select: function (index){
        lyrics_board.clear()
        this.highlight(index);
        lyrics_board.set(lyrics[index])
    },
    
    populate: function (lyrics) {
        lyrics = lyrics == null ? [] : lyrics
    
        this.reset();
        
        lyrics.forEach((e, i) => {
            this.set_data(e, i);
        });
    
        return true
    }
}

lyrics_board = {
    clear: () => {
        $(ids.lyric_title).html('?')
        $(ids.lyric_content).html('?')
    },
    set: (data) => {
        $(ids.lyric_title).text(data.title)
        $(ids.lyric_content).text(data.content)
    }
}



animations = {
    done: () => {
        $("#done").removeClass("hidden")

        setTimeout(() => {$("#done").addClass("hidden")}, 5000)
    },
    loading: {
        start: x => $("#loader").removeClass("hidden"),
        end: x => $("#loader").addClass("hidden")
    }
}

mock_api = function(){
    return new Promise((resolve) => {
        setTimeout(()=>{
            resolve(lyrics);
        }, 5000);
    });
}

$(document).ready(function () {

    $(ids.lyrics_list + ' li').on("click", function(){
        var index = $(ids.lyrics_list + ' li').index(this);
        lyrics_list.select(index);
    })


    $("form").submit(function (event) {

        animations.loading.start()
        lyrics_list.reset()
        
    //   var formData = {
    //     name: $("#name").val(),
    //     email: $("#email").val(),
    //     superheroAlias: $("#superheroAlias").val(),
    //   };
  
    //   $.ajax({
    //     type: "POST",
    //     url: "process.php",
    //     data: formData,
    //     dataType: "json",
    //     encode: true,
    //   }).done(function (data) {
    //     console.log(data);
    //   });


        mock_api().then(()=>{
            lyrics_list.populate(lyrics);
            lyrics_list.select(0);
            animations.done();
            animations.loading.end()
        },
        () => { 
            animations.loading.end()
        });
   
    
        event.preventDefault();
    });
  });