$(function() {
    // XSS対策用
    function escapeHtml(str) {
        return str.replace(/[&<>"']/g, function(m) {
            return ({
                '&':'&amp;',
                '<':'&lt;',
                '>':'&gt;',
                '"':'&quot;',
                "'":'&#39;'
            })[m];
        });
    }

    // いいねボタン
    $(document).on("click", ".like-btn", function() {
        const btn = $(this);
        const postId = btn.data("post-id");  // .data()を推奨
        const heart = btn.find(".heart");
        const countSpan = btn.find(".like-count");
        let count = parseInt(countSpan.text()) || 0;

        $.post(`/like/${postId}`, function(res) {
            if(res.liked){
                heart.addClass("liked");
                countSpan.text(count + 1);
            } else {
                heart.removeClass("liked");
                countSpan.text(Math.max(count - 1, 0));
            }
            heart.addClass("animate");
            setTimeout(() => heart.removeClass("animate"), 300);
        }).fail(function(err){
            alert(err.responseJSON ? err.responseJSON.error : "送信エラー");
        });
    });

    // コメント送信
    $(document).on("submit", ".comment-form", function(e){
        e.preventDefault();
        const form = $(this);
        const postId = form.data("post-id");
        const contentInput = form.find("input[name='content']");
        const content = contentInput.val().trim();
        if(!content) return;

        $.post(`/comment/${postId}`, { content: content }, function(res) {
            const postDiv = form.closest(".post-item");
            const commentsDiv = postDiv.find(".comments");
            commentsDiv.append(`<p><b>${escapeHtml(res.user)}:</b> ${escapeHtml(res.content)}</p>`);
            contentInput.val("").focus();
            // 最新コメントを見える位置にスクロール
            commentsDiv.scrollTop(commentsDiv[0].scrollHeight);
        }).fail(function(err){
            alert(err.responseJSON ? err.responseJSON.error : "送信エラー");
        });
    });
});
