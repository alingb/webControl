$(document).ready(function () {
    toastr.options.positionClass = 'toast-top-center';
    var oFileTable = new FileTableInit();
    oFileTable.Init();
});

var FileTableInit = function () {
    var oFileTableInit = new Object();
    //初始化Table
    oFileTableInit.Init = function () {
        $('#luk_service').bootstrapTable({
            url: '/lukServer/lukServiceMsg',         //请求后台的URL（*）
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
            rowStyle: function (row, index) {
                //这里有5个取值代表5中颜色['active', 'success', 'info', 'warning', 'danger'];
                var strclass = "";
                if (row.serverStat == "True") {
                    strclass = 'success';//还有一个active
                }
                else if (row.serverStat == "Flase") {
                    strclass = 'warning';
                }
                else {
                    return {};
                }
                return { classes: strclass }
            },
            columns: [{
                checkbox: true
            }, {
                field: 'id',
                title: 'ID',
                // visible: false
            }, {
                field: 'macAddr',
                title: 'MAC地址'
            },{
                field: 'serverStat',
                title: '服务状态'
            },{
                field: 'mechineStat',
                title: '机器状态'
            },{
                field: 'mechineSensor',
                title: '机器温度',
                visible: false
            },{
                field: 'ipAddr',
                title: 'IP地址'
            },{
                field: 'username',
                title: '用户名称',
                visible: false
            },{
                field: 'runTime',
                title: '提交时间'
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

function buttonexec() {
    $("#reset_luk").click(function () {
        var luk_info = $("#luk_service").val();
        $.ajax({
            type: "post",
            url: "/lukServer/lukAddUser",
            data: {"data": JSON.stringify({"user": luk_info, "state": "reset", "name": "luk"})},
            success: function (data, status) {
                toastr.success('矿机重启成功');
                $("#luk_service").bootstrapTable('refresh');
            },
            error: function (data, status) {
                toastr.error('执行失败');
                return false;
            }

        })
    });
    $("#off_luk").click(function () {
        var luk_info = $("#luk_service").val();
        $.ajax({
            type: "post",
            url: "/lukServer/lukAddUser",
            data: {"data": JSON.stringify({"user": luk_info, "state": "off", "name": "luk"})},
            success: function (data, status) {
                toastr.success('矿机关闭成功');11
                $("#luk_service").bootstrapTable('refresh');
            },
            error: function (data, status) {
                toastr.error('执行失败');
                return false;
            }

        })
    });
    $("#off_service").click(function () {
        var luk_info = $("#luk_service").val();
        $.ajax({
            type: "post",
            url: "/lukServer/lukAddUser",
            data: {"data": JSON.stringify({"user": luk_info, "state": "off", "name": "service"})},
            success: function (data, status) {
                toastr.success('程序关闭成功');
                $("#luk_service").bootstrapTable('refresh');
            },
            error: function (data, status) {
                toastr.error('执行失败');
                return false;
            }

        })
    });
    $("#reset_service").click(function () {
        var luk_info = $("#luk_service").val();
        $.ajax({
            type: "post",
            url: "/lukServer/lukAddUser",
            data: {"data": JSON.stringify({"user": luk_info, "state": "reset", "name": "service"})},
            success: function (data, status) {
                toastr.success('程序重启成功');
                $("#luk_service").bootstrapTable('refresh');
            },
            error: function (data, status) {
                toastr.error('执行失败');
                return false;
            }

        })
    });
}