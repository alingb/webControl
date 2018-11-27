$(document).ready(function () {
    toastr.options.positionClass = 'toast-top-center';
    var oFileTable = new FileTableInit();
    oFileTable.Init();
    addclass();
    buttonStart();
    setInterval(function() {
        $("#bios").bootstrapTable('refresh');
}, 10000);
});


function addclass() {
    $('#tv').addClass('active');
    $("#tv1").addClass('active')
}

var FileTableInit = function () {
    var oFileTableInit = new Object();
    //初始化Table
    oFileTableInit.Init = function () {
        $('#bios').bootstrapTable({
            url: '/control/serverinfo?state=wait',         //请求后台的URL（*）
            method: 'get',    //请求方式（*）
            contentType:"application/x-www-form-urlencoded; charset=UTF-8",
            toolbar: '#toolbar',                //工具按钮用哪个容器
            striped: true,                      //是否显示行间隔色
            cache: false,                       //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            pagination: true,                   //是否显示分页（*）
            sortable: true,                     //是否启用排序
            sortOrder: "asc",                   //排序方式 asc desc
            sortName: "id",
            queryParams: oFileTableInit.queryParams,//传递参数（*）
            sidePagination: "server",           //分页方式：client客户端分页，server服务端分页（*）
            pageNumber: 1,                       //初始化加载第一页，默认第一页
            pageSize: 25,                       //每页的记录行数（*）
            pageList: [10, 25, 50, 100],        //可供选择的每页的行数（*）
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

                if (row.change_stat.indexOf("完成") !== -1) {
                    strclass = 'success';//还有一个active
                }
                else if (row.change_stat.indexOf("执行中") !== -1) {
                    strclass = 'info';
                }
                else if (row.change_stat.indexOf("失败") !== -1) {
                    strclass = 'danger';
                }
                else {
                    strclass = "info";
                }
                return {classes: strclass}
            },
            columns: [{
                checkbox: true
            }, {
                field: 'id',
                title: 'ID',
                sortable: true,
                visible: false
            }, {
                field: 'ip',
                title: 'IP',
                sortable: true,
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
                visible: false,
                sortable: true
            }, {
                field: 'bios',
                title: 'BIOS',
                sortable: true
            }, {
                field: 'bmc',
                title: 'BMC',
                sortable: true
            }, {
                field: 'stress_test',
                title: '运行状态',
                sortable: true
            },{
                field: 'change_stat',
                title: '执行状态',
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


function buttonStart() {
    $("#bios_selectpicker").bind("change",function () {
        let dataval = $(this).val();
        if (dataval === 0 ){
            $("#bios_name").hide();
        }
        else {
            $("#bios_name").show();
        }
        $.ajax({
            type: "post",
            url: "/control/infopaser",
            data:{"val": dataval},
            success:function (data, status) {
                 if (status === "success") {
                     data = jQuery.parseJSON(data);
                     $('#bios_name_selectpicker').find("option").remove();
                     for (var i = 0; i < data.length; i++) {
                         $("#bios_name_selectpicker").append($("<option></option>").attr("value", data[i]).attr("data-content", "<span class='label label-info'>" +  data[i] + "</span>").text(data[i])).trigger("change");
                         $('#bios_name_selectpicker').selectpicker('val', '').trigger("change");
                         $('#bios_name_selectpicker').selectpicker('refresh');
                     }
                 }
            }
        })
    });
    $("#fru_selectpicker").bind("change",function () {
        let dataval = $(this).val();
        if (dataval === 0 ){
            $("#fru_name").hide();
        }
        else {
            $("#fru_name").show();
        }
        $.ajax({
            type: "post",
            url: "/control/infopaser",
            data:{"val": dataval},
            success:function (data, status) {
                 if (status === "success") {
                     data = jQuery.parseJSON(data);
                     $('#fru_name_selectpicker').find("option").remove();
                     for (var i = 0; i < data.length; i++) {
                         $("#fru_name_selectpicker").append($("<option></option>").attr("value", data[i]).attr("data-content", "<span class='label label-info'>" +  data[i] + "</span>").text(data[i])).trigger("change");
                         $('#fru_name_selectpicker').selectpicker('val', '').trigger("change");
                         $('#fru_name_selectpicker').selectpicker('refresh');
                     }
                 }
            }
        })
    });
    let url = "/control/mkexec";
    $("#bios_button").click(function () {
            let table = $("#bios").bootstrapTable('getSelections');
            if (table.length <= 0) {
                toastr.error("请选择需要执行的设备")
            }
            else {
                $("#myModal").modal();
                $("#myModal").find("#myModalLabel").text("请选择BIOS信息");
                $("#bios_submit").click(function () {
                    let name = $("#bios_selectpicker").val();
                    let name1 = $("#bios_name_selectpicker").val();
                    $.ajax({
                        type: "post",
                        url: url,
                        data: {"state": "bios", "name": name, "name1": name1, "msg": JSON.stringify(table)},
                        // success: function (data, status) {
                        //     if (status === "success") {
                        //         toastr.success('BIOS Execute sucess!');
                        //         $("#bios").bootstrapTable('refresh');
                        //     }
                        //
                        // },
                        error: function () {
                            toastr.error('BIOS Execute Error!');
                        }
                    });
                    $("#bios_button").attr({"disabled": "disabled"});
                    toastr.success('BIOS Execute sucess!');
                    $("#bios_close").click(function () {
                        setTimeout(function () {
                            $("#bios").bootstrapTable('refresh');
                        }, 3000)
                    });
                });
            }
        }
    );

    $("#bmc_button").click(function () {
            let table = $("#bios").bootstrapTable('getSelections');
            if (table.length <= 0) {
                toastr.error("请选择需要执行的设备")
            }
            else {
                $("#myModal").modal();
                $("#myModal").find("#myModalLabel").text("请选择BMC信息");
                $("#bios_submit").click(function () {
                    let name = $("#bios_selectpicker").val();
                    let name1 = $("#bios_name_selectpicker").val();
                    $.ajax({
                        type: "post",
                        url: url,
                        data: {"state": "bmc", "name": name, "name1": name1, "msg": JSON.stringify(table)},
                        // success: function (data, status) {
                        //     if (status === "success") {
                        //         toastr.success('BIOS Execute sucess!');
                        //         $("#bios").bootstrapTable('refresh');
                        //     }
                        //
                        // },
                        error: function () {
                            toastr.error('BMC Execute Error!');
                        }
                    });
                    $("#bmc_button").attr({"disabled": "disabled"});
                    toastr.success('BMC Execute sucess!');
                    $("#bios_close").click(function () {
                        setTimeout(function () {
                            $("#bios").bootstrapTable('refresh');
                        }, 3000)
                    });
                });
            }
        }
    );

    $("#fru_button").click(function () {
        let table = $("#bios").bootstrapTable('getSelections');
        if (table.length <= 0) {
            toastr.error("请选择需要执行的设备")
        } else {
            $('#myModal2').modal();
            $("#myModal2").find("#fru_msg").val("");
            let data = JSON.stringify(table);
            $("#fru_submit").click(function () {
                    if (data.length <= 0) {
                        toastr.error("请选择需要执行的设备");
                        return;
                    }
                    $("#data").val(data);
                    $("#fru_form").submit();
                    $("#fru_close").click(function () {
                        setTimeout(function () {
                            $("#bios").bootstrapTable('refresh');
                        }, 3000)
                    });
                }
            );
        }
    })
}