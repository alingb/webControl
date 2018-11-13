$(document).ready(function () {
    toastr.options.positionClass = 'toast-top-center';
    var oFileTable = new FileTableInit();
    oFileTable.Init();
    $("#link2").addClass("active");
});

var FileTableInit = function () {
    var oFileTableInit = new Object();
    //初始化Table
    oFileTableInit.Init = function () {
        $('#serverdetail').bootstrapTable({
            url: '/control/serverinfo',         //请求后台的URL（*）
            method: 'get',    //请求方式（*）
            toolbar: '#toolbar',                //工具按钮用哪个容器
            striped: true,                      //是否显示行间隔色
            cache: false,                       //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            pagination: true,                   //是否显示分页（*）
            sortable: true,                     //是否启用排序
            sortOrder: "desc",                   //排序方式 asc desc
            sortName: "id",
            queryParams: oFileTableInit.queryParams,//传递参数（*）
            sidePagination: "server",           //分页方式：client客户端分页，server服务端分页（*）
            pageNumber: 1,                       //初始化加载第一页，默认第一页
            pageSize: 25,                       //每页的记录行数（*）
            pageList: [10, 25, 50, 100, 200, 500, 1000],        //可供选择的每页的行数（*）
            search: true,                       //是否显示表格搜索，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
            searchOnEnterKey: true,
            showExport: true,
            exportDataType: "selected", //默认basic：只导出当前页的表格数据；all：导出所有数据；selected：导出选中的数据
            strictSearch: true,
            paginationLoop: false,
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
                if (row.stress_test == "running") {
                    strclass = 'success';//还有一个active
                }
                else if (row.stress_test == 75) {
                    strclass = 'warning';
                }
                else {
                    strclass = 'warning'
                }
                return {classes: strclass}
            },
            // responseHandler: function (data) {
            //     return data.rows;
            // },
            columns: [{
                checkbox: true
            }, {
                field: 'id',
                title: 'ID',
                sortable: true,
                formatter:linkFormatter
                // visible: false
            }, {
                field: 'sn',
                title: 'SN',
                sortable: true
            }, {
                field: 'sn_1',
                title: 'SN1',
                sortable: true
            }, {
                field: 'name',
                title: 'NAME',
                sortable: true
            }, {
                field: 'name1',
                title: 'NAME1',
                sortable: true
            }, {
                field: 'family',
                title: 'FAMILY',
                sortable: true
            }, {
                field: 'status',
                title: '状态',
                sortable: true,
                formatter: colorFormatter
            }, {
                field: 'bios',
                title: 'BIOS',
                sortable: true
            },{
                field: 'bmc',
                title: 'BMC',
                sortable: true
            },{
                field: 'stress_test',
                title: '运行状态',
                sortable: true
            },],
        });
    };
    //得到查询的参数
    oFileTableInit.queryParams = function (params) {
        var temp = {   //这里的键的名字和控制器的变量名必须一直，这边改动，控制器也需要改成一样的
            limit: params.limit,   //页面大小
            offset: params.offset,  //页码
            sort: params.sort,      //排序列名
            sortOrder: params.order, //排位命令（desc，asc）
            search: params.search
        };
        return temp;
    };
    return oFileTableInit;
};

function linkFormatter(value, row, index) {
            return "<a href='" + value + "' title='单击打开连接' target='_blank'>" + value + "</a>";
        }

function colorFormatter(value) {
            if (value == "pass") { color = 'Green'; }
            else if (value == "complete") { color = 'Gray'; }
            else if (value == "no check data") { color = 'Black'; }
            else { color = 'Red'; }

            return '<div  style="color: ' + color + '">' + '<b>'+ value + '</b>' + '</div>';
        }