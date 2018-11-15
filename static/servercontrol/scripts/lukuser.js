$(document).ready(function () {
    toastr.options.positionClass = 'toast-top-center';
    var oFileTable = new FileTableInit();
    oFileTable.Init();
    buttonexec();
    userUpdate();
});

var FileTableInit = function () {
    var oFileTableInit = new Object();
    //初始化Table
    oFileTableInit.Init = function () {
        $('#luk_user').bootstrapTable({
            url: '/lukServer/lukServerMsg',         //请求后台的URL（*）
            method: 'get',    //请求方式（*）
            toolbar: '#toolbar',                //工具按钮用哪个容器
            striped: true,                      //是否显示行间隔色
            cache: false,                       //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            pagination: true,                   //是否显示分页（*）
            sortable: true,                     //是否启用排序
            sortOrder: "asc",                   //排序方式
            queryParams: oFileTableInit.queryParams,//传递参数（*）
            sidePagination: "server",           //分页方式：client客户端分页，server服务端分页（*）
            pageNumber: 1,                       //初始化加载第一页，默认第一页
            pageSize: 10,                       //每页的记录行数（*）
            pageList: [10, 25, 50, 100],        //可供选择的每页的行数（*）
            search: false,                       //是否显示表格搜索，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
            showExport: true,
            exportDataType: "basic",
            strictSearch: true,
            // showColumns: true,                  //是否显示所有的列
            showRefresh: true,                  //是否显示刷新按钮
            minimumCountColumns: 2,             //最少允许的列数
            clickToSelect: true,                //是否启用点击选中行
            // height: 500,                        //行高，如果没有设置height属性，表格自动根据记录条数觉得表格高度
            // uniqueId: "id",                     //每一行的唯一标识，一般为主键列
            // showToggle: true,                    //是否显示详细视图和列表视图的切换按钮
            // cardView: false,                    //是否显示详细视图
            // detailView: false,                   //是否显示父子表
            columns: [{
                checkbox: true
            }, {
                field: 'id',
                title: 'ID',
                // visible: false
            }, {
                field: 'user',
                title: '用户'
            },],
        });
    };
        //得到查询的参数
    oFileTableInit.queryParams = function (params) {
        var temp = {   //这里的键的名字和控制器的变量名必须一直，这边改动，控制器也需要改成一样的
            limit: params.limit,   //页面大小
            offset: params.offset,  //页码
        };
        return temp;
    };
    return oFileTableInit;
};

function userUpdate() {
    $("#user_update").click(function () {
        var a = $("#luk_user").bootstrapTable('getSelections');
        if (a.length <= 0) {
            toastr.warning("请选择需要设置的用户")
        } else {
            var b = JSON.stringify(a);
            console.log(b);
            var url = "/lukServer/lukUserChange";
            $.ajax({
                dataType: "json",
                traditional: true,//这使json格式的字符不会被转码
                data: {"data": b},
                type: "post",
                url: url,
                success: function (data, status) {
                    toastr.success(status);
                },
                error: function (data, status) {
                    toastr.error(status);
                }
            });
        }

    });

}

function buttonexec() {
    $("#user_submit").click(function () {
        var user_name = $("#user_name").val();
        $.ajax({
            type: "post",
            url: "/lukServer/lukAddUser",
            data: {"data": JSON.stringify({"user": user_name})},
            success: function (data, status) {
                toastr.success('用户创建成功');
                $("#luk_user").bootstrapTable('refresh');
                $("#user_close").click();
            },
            error: function (data, status) {
                toastr.error('用户已存在');
                return false;
            }

        })
    });
}