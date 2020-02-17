<template>
    <div id="Content">
        <el-dialog
            id="hello"
            title="肿瘤辅助诊断系统使用须知"
            :visible.sync="centerDialogVisible"
            width="65%"
            :before-close="handleClose"
        >
            <el-steps :active="5" finish-status="process ">
                <el-step title="步骤1" style="width:280px;padding-left: 50px">
                    <template slot="description">
                        <p style="font-size: 16px">下载测试CT文件文件</p>
                        <br>
                        <br>
                    </template>
                </el-step>
                <el-step title="步骤2" style="width:260px;margin-left:-5px;">
                    <template slot="description">
                        <p>上传CT图像至服务器</p>
                        <p>使用训练的模型预测肿瘤区域</p>
                        <p>并返回肿瘤区域特征</p>
                    </template>
                </el-step>
                <el-step title="步骤3" style="width:260px;margin-left:-5px;">
                    <template slot="description">
                        <div>
                            <p>根据预测的肿瘤区域和特征</p>
                            <p>进行辅助诊断</p>
                            <br>
                        </div>
                    </template>
                </el-step>
            </el-steps>
            <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="welcome">下载测试CT图像</el-button>
      </span>
        </el-dialog>
        <el-dialog
            title="AI预测中"
            :visible.sync="dialogTableVisible"
            :show-close="false"
            :close-on-press-escape="false"
            :append-to-body="true"
            :close-on-click-modal="false"
            :center="true"
        >
            <el-progress :percentage="percentage"></el-progress>
            <span slot="footer" class="dialog-footer">非GPU学生服务器性能有限，请耐心等待约一分钟</span>
        </el-dialog>

        <div id="aside">
            <!-- 查看病人信息 -->
            <el-card class="box-card" style="width:250px;height:350px">
                <div slot="header" class="clearfix">
                    <span>病人信息</span>
                </div>
                <div v-for="(value,name) in patient" :key="name" class="text item">
                    <h3 style="font-weight:normal;">{{name}}:{{value}}</h3>
                </div>
            </el-card>

            <!-- 步骤条：下载 上传 -->
            <el-card
                class="box-card"
                body-style="padding: 15px 5px 15px 10px"
                style="width:250px;height:500px;margin-top:50px;"
            >
                <div slot="header" class="clearfix" style="text-align:center;">
                    <span class="steps" style="letter-spacing: 7px;">诊断测试步骤</span>
                </div>
                <div style="height: 600px;" class="step_1">
                    <el-steps direction="vertical" :active="active" finish-status="success">
                        <el-step style="height: 120px;" title="步骤 1">
                            <template slot="description" style="font-size: 10px!important;">
                                下载测试CT文件
                                <!-- 下载文件 -->
                                <el-button
                                    type="primary"
                                    icon="el-icon-download"
                                    @click="downTemplate"
                                    class="download_bt"
                                >下载
                                </el-button>
                            </template>
                        </el-step>
                        <el-step style="height: 150px;" title="步骤 2">
                            <template slot="description">
                                <!-- 上传文件 -->
                                上传CT图像至服务器，使用训练的模型预测肿瘤区域并返回肿瘤区域特征
                                <el-button type="primary" icon="el-icon-upload" class="download_bt">上传</el-button>
                                <input class="file" name="file" type="file" @change="update">
                            </template>
                        </el-step>

                        <!-- 获得图像 -->
                        <el-step title="获得图像及特征" style="height: 200px;">
                            <template slot="description"></template>
                        </el-step>
                    </el-steps>
                </div>
            </el-card>
        </div>
        <!-- 上传返回信息部分：原CT图部分  标出肿瘤的CT图像 图像特征-->
        <div id="CT">
            <!-- CT图像 -->
            <div id="CT_image">
                <!-- 原CT图 -->
                <el-card
                    id="CT_image_1"
                    class="box-card"
                    style="border-radius: 8px;width:800px;height:360px;margin-bottom:-30px;"
                >
                    <div class="demo-image__preview1">
                        <div
                            v-loading="loading"
                            element-loading-text="上传图片中"
                            element-loading-spinner="el-icon-loading"
                        >
                            <el-image
                                :src="url_1"
                                class="image_1"
                                :preview-src-list="srcList"
                                style="border-radius: 3px 3px 0 0"
                            >
                                <div slot="error">
                                    <div slot="placeholder" class="error">
                                        <el-button
                                            v-show="showbutton"
                                            type="primary"
                                            icon="el-icon-upload"
                                            class="download_bt"
                                            v-on:click="true_upload"
                                        >
                                            上传dcm文件
                                            <input
                                                ref="upload"
                                                style="display: none"
                                                name="file"
                                                type="file"
                                                @change="update"
                                            >
                                        </el-button>
                                    </div>
                                </div>
                            </el-image>
                        </div>
                        <!-- 原CT图文字 -->
                        <div class="img_info_1" style="border-radius:0 0 5px 5px;">
                            <span style="color:white;letter-spacing:6px;">原CT图像</span>
                        </div>
                    </div>
                    <!-- 标出肿瘤的CT图像 -->
                    <div class="demo-image__preview2">
                        <div
                            v-loading="loading"
                            element-loading-text="处理中,请耐心等待"
                            element-loading-spinner="el-icon-loading"
                        >
                            <el-image
                                :src="url_2"
                                class="image_1"
                                :preview-src-list="srcList1"
                                style="border-radius: 3px 3px 0 0;"
                            >
                                <div slot="error">
                                    <div slot="placeholder" class="error">{{wait_return}}</div>
                                </div>
                            </el-image>
                        </div>
                        <!-- 标出肿瘤的CT图像文字 -->
                        <div class="img_info_1" style="border-radius: 0 0 5px 5px;">
                            <span style="color:white;letter-spacing:4px;">标出肿瘤的CT图像</span>
                        </div>
                    </div>
                </el-card>
            </div>


            <!-- 分割线 -->

            <!-- 图像特征部分 -->
            <div id="info_patient">
                <!-- 卡片放置表格 -->
                <el-card style="border-radius: 8px;">
                    <div slot="header" class="clearfix">
                        <span>肿瘤区域特征值</span>
                        <el-button
                            style="margin-left: 35px"
                            v-show="!showbutton"
                            type="primary"
                            icon="el-icon-upload"
                            class="download_bt"
                            v-on:click="true_upload2"
                        >
                            重新选择图像
                            <input
                                ref="upload2"
                                style="display: none"
                                name="file"
                                type="file"
                                @change="update"
                            >
                        </el-button>
                    </div>


                    <el-tabs v-model="activeName" @tab-click="handleClick">
                        <el-tab-pane label="肿瘤区域特征值" name="first">
                            <!-- 表格存放特征值 -->
                            <el-table
                                :data="feature_list"
                                height="390"
                                border
                                style="width:750px;text-align:center;"
                                v-loading="loading"
                                element-loading-text="数据正在处理中，请耐心等待"
                                element-loading-spinner="el-icon-loading"
                                lazy
                            >
                                <el-table-column label="Feature" width="250px">
                                    <template slot-scope="scope">
                                        <span>{{scope.row[2]}}</span>
                                    </template>
                                </el-table-column>
                                <!-- 特征名 -->
                                <el-table-column label="特征名" width="250px">
                                    <template slot-scope="scope">
                                        <span>{{scope.row[0]}}</span>
                                    </template>
                                </el-table-column>

                                <!-- 特征值 -->
                                <el-table-column label="特征值" width="250px">
                                    <template slot-scope="scope">
                                        <span>{{scope.row[1]}}</span>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </el-tab-pane>
                        <el-tab-pane label="面积对比" name="second" style="width:750px;height:390px;">
                            <div id="areaCompare">
                                <el-table

                                    :data="feature_list"
                                    height="390"
                                    border
                                    style="width:750px;text-align:center;"
                                    v-loading="loading"
                                    element-loading-text="数据正在处理中，请耐心等待"
                                    element-loading-spinner="el-icon-loading"
                                >
                                    <el-table-column label="Feature" width="250px">
                                        <template slot-scope="scope">
                                            <span>{{scope.row[2]}}</span>
                                        </template>
                                    </el-table-column>
                                    <!-- 特征名 -->
                                    <el-table-column label="特征名" width="250px">
                                        <template slot-scope="scope">
                                            <span>{{scope.row[0]}}</span>
                                        </template>
                                    </el-table-column>

                                    <!-- 特征值 -->
                                    <el-table-column label="特征值" width="250px">
                                        <template slot-scope="scope">
                                            <span>{{scope.row[1]}}</span>
                                        </template>
                                    </el-table-column>
                                </el-table>
                            </div>
                            <div id="area" style="width: 750px;height:400px;margin-bottom:20px;"></div>
                        </el-tab-pane>
                        <el-tab-pane label="周长对比" name="third" style="width:750px;height:390px;">
                            <div id="perimeterCompare">
                                <el-table

                                    :data="feature_list"
                                    height="390"
                                    border
                                    style="width:750px;text-align:center;"
                                    v-loading="loading"
                                    element-loading-text="数据正在处理中，请耐心等待"
                                    element-loading-spinner="el-icon-loading"
                                >
                                    <el-table-column label="Feature" width="250px">
                                        <template slot-scope="scope">
                                            <span>{{scope.row[2]}}</span>
                                        </template>
                                    </el-table-column>
                                    <!-- 特征名 -->
                                    <el-table-column label="特征名" width="250px">
                                        <template slot-scope="scope">
                                            <span>{{scope.row[0]}}</span>
                                        </template>
                                    </el-table-column>

                                    <!-- 特征值 -->
                                    <el-table-column label="特征值" width="250px">
                                        <template slot-scope="scope">
                                            <span>{{scope.row[1]}}</span>
                                        </template>
                                    </el-table-column>
                                </el-table>
                            </div>

                            <div id="perimeter" style="width: 750px;height:400px;margin-bottom:20px;"></div>
                        </el-tab-pane>
                    </el-tabs>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from "axios";

    export default {
        name: "Content",
        data() {
            return {
                // server_url:'http://58.87.66.50:5003',
                server_url:'http://127.0.0.1:5003',
                perimeter_picture_data: 0,
                area_picture_data: 0,
                activeName: "first",
                active: 0,
                centerDialogVisible: true,
                url_1: "",
                url_2: "",
                textarea: "",
                srcList: [],
                srcList1: [],
                feature_list: [],
                feature_list_1: [],
                feat_list: [],
                url: "",
                visible: false,
                activeName: "second",
                wait_return: "等待上传",
                wait_upload: "等待上传",
                loading: false,
                table: false,
                isNav: false,
                showbutton: true,
                percentage: 0,
                fullscreenLoading: false,
                opacitys: {
                    opacity: 0
                },
                dialogTableVisible: false,
                patient: {
                    ID: "20190001",
                    姓名: "李明",
                    性别: "男",
                    年龄: "29",
                    电话: "13220986785",
                    部位: "直肠"
                }
            };
        },
        created: function () {
            document.title = '肿瘤辅助诊断系统';
        },
        methods: {
            true_upload() {
                this.$refs.upload.click();
            },
            true_upload2() {
                this.$refs.upload2.click();
            },
            handleClose(done) {
                this.$confirm("确认关闭？")
                    .then(_ => {
                        done();
                    })
                    .catch(_ => {
                    });
            },
            next() {
                this.active++;
            },
            // 获得目标文件
            getObjectURL(file) {
                var url = null;
                if (window.createObjcectURL != undefined) {
                    url = window.createOjcectURL(file);
                } else if (window.URL != undefined) {
                    url = window.URL.createObjectURL(file);
                } else if (window.webkitURL != undefined) {
                    url = window.webkitURL.createObjectURL(file);
                }
                return url;
            },
            // 点击切换
            handleClick(tab, event) {
                if (tab.name == "second") {
                    this.drawChart();
                    var myChart_area = this.$echarts.init(document.getElementById('area'));
                    // myChart_area.clear();
                    myChart_area.setOption({
                        xAxis: {
                            type: "category",
                            data: ["1", "2", "3", "4", "5", "6", "7", "8"]
                        },
                        yAxis: {
                            type: "value",
                            name: "面积"
                        },
                        areaStyle: {},
                        legend: {
                            data: [""]
                        },
                        series: [
                            {
                                // 根据名字对应到相应的系列
                                name: "面积",
                                type: "line",
                                data: [
                                    1300,
                                    1290,
                                    1272,
                                    1123.5,
                                    1123,
                                    1092,
                                    1086,
                                    this.area_picture_data
                                ]
                            }
                        ]
                    });
                } else if (tab.name == "third") {
                    this.drawChart();
                    var myChart_perimeter = this.$echarts.init(document.getElementById('perimeter'));
                    myChart_perimeter.setOption({
                        xAxis: {
                            type: "category",
                            data: ["1", "2", "3", "4", "5", "6", "7", "8"]
                        },
                        yAxis: {
                            type: "value",
                            name: "周长"
                        },
                        areaStyle: {},
                        series: [
                            {
                                // 根据名字对应到相应的系列
                                name: "周长",
                                type: "line",
                                data: [
                                    250,
                                    243,
                                    227,
                                    201,
                                    197,
                                    170,
                                    159,
                                    this.perimeter_picture_data
                                ]
                            }
                        ]
                    });
                }
            },
            // 上传dcm文件
            update(e) {
                this.percentage = 0;
                this.dialogTableVisible = true;
                this.url_1 = "";
                this.url_2 = "";
                this.srcList = [];
                this.srcList1 = [];
                this.wait_return = "";
                this.wait_upload = "";
                this.feature_list = [];
                let myChart_area = this.$echarts.init(document.getElementById("area"));
                myChart_area.setOption({
                    series: [
                        {
                            data: [""]
                        }
                    ]
                });
                this.feat_list = [];
                this.fullscreenLoading = true;
                this.loading = true;
                this.showbutton = false;
                let file = e.target.files[0];
                this.url_1 = this.$options.methods.getObjectURL(file);
                let param = new FormData(); //创建form对象
                param.append("file", file, file.name); //通过append向form对象添加数据
                // console.log(param.get("file")); //FormData私有类对象，访问不到，可以通过get判断值是否传进去
                //todo aaaa
                var timer = setInterval(() => {
                    this.myFunc();
                }, 30);
                let config = {
                    headers: {"Content-Type": "multipart/form-data"}
                }; //添加请求头
                axios
                    .post(this.server_url+"/upload", param, config)
                    .then(response => {
                        this.percentage = 100;
                        clearInterval(timer);
                        this.url_1 = response.data.image_url;
                        this.srcList.push(this.url_1);
                        this.url_2 = response.data.draw_url;
                        this.srcList1.push(this.url_2);
                        this.fullscreenLoading = false;
                        this.loading = false;

                        this.feat_list = Object.keys(response.data.image_info);

                        for (var i = 0; i < this.feat_list.length; i++) {
                            response.data.image_info[this.feat_list[i]][2] = this.feat_list[i];
                            this.feature_list.push(response.data.image_info[this.feat_list[i]]);
                        }

                        this.feature_list.push(response.data.image_info);
                        this.feature_list_1 = this.feature_list[0];
                        JSON.stringify(response.data.image_info, (key, value) => {
                            console.log(key);
                            console.log(value);
                        });
                        this.dialogTableVisible = false;
                        this.percentage = 0;
                        this.notice1();
                        var areaCompare = document.getElementById("areaCompare");
                        areaCompare.style.display = "none";
                        var areaCompare = document.getElementById("perimeterCompare");
                        areaCompare.style.display = "none";
                        let myChart_area = this.$echarts.init(
                            document.getElementById("area")
                        );
                        let myChart_perimeter = this.$echarts.init(
                            document.getElementById("perimeter")
                        );
                        this.perimeter_picture_data = parseInt(response.data.image_info["perimeter"][1]);
                        this.area_picture_data = parseInt(response.data.image_info["area"][1]);
                        myChart_area.setOption({
                            xAxis: {
                                type: "category",
                                data: ["1", "2", "3", "4", "5", "6", "7", "8"]
                            },
                            yAxis: {
                                type: "value",
                                name: "面积"
                            },
                            areaStyle: {},
                            legend: {
                                data: [""]
                            },
                            series: [
                                {
                                    // 根据名字对应到相应的系列
                                    name: "面积",
                                    type: "line",
                                    data: [
                                        1300,
                                        1290,
                                        1272,
                                        1123.5,
                                        1123,
                                        1092,
                                        1086,
                                        response.data.image_info["area"][1]
                                    ]
                                }
                            ]
                        });

                        myChart_perimeter.setOption({
                            xAxis: {
                                type: "category",
                                data: ["1", "2", "3", "4", "5", "6", "7", "8"]
                            },
                            yAxis: {
                                type: "value",
                                name: "周长"
                            },
                            areaStyle: {},
                            series: [
                                {
                                    // 根据名字对应到相应的系列
                                    name: "周长",
                                    type: "line",
                                    data: [
                                        250,
                                        243,
                                        227,
                                        201,
                                        197,
                                        170,
                                        159,
                                        response.data.image_info["perimeter"]
                                    ]
                                }
                            ]
                        });
                    });
            },
            // 下载 点击按钮 从远程接口获取文件
            downTemplate() {
                axios({
                    method: "get",
                    url:
                        "https://cso1-1254043908.cos.ap-beijing.myqcloud.com/ct/testfile.7z",
                    responseType: "blob"
                }).then(res => {
                    this.downloads(res.data, res.headers.filename);

                    if (res.status === 200) {
                        this.$message({
                            message: "下载成功",
                            type: "success"
                        });
                        if (this.active == 0) {
                            this.next();
                        }
                    } else {
                        this.$message({
                            showClose: true,
                            message: "下载失败，请重试",
                            type: "error"
                        });
                    }
                });
            },
            myFunc() {
                if (this.percentage + 33 < 99) {
                    this.percentage = this.percentage + 33;
                    console.log(this.percentage);
                } else {
                    this.percentage = 99;
                }
            },
            drawChart() {
                // 基于准备好的dom，初始化echarts实例
                let myChart_area = this.$echarts.init(document.getElementById("area"));
                let myChart_perimeter = this.$echarts.init(
                    document.getElementById("perimeter")
                );
                // 指定图表的配置项和数据
                myChart_area.setOption({
                    title: {
                        text: "肿瘤面积变化",
                        subtext: "Tumor Area Change",
                        left: "center"
                    },
                    legend: {
                        data: [""]
                    },
                    tooltip: {},

                    grid: {
                        //显示数据的图表位于当前canvas的坐标轴
                        x: 50,
                        y: 55,
                        x2: 50,
                        y2: 60,
                        borderWidth: 1
                    },

                    toolbox: {
                        show: true,
                        feature: {
                            dataZoom: {
                                yAxisIndex: "none"
                            },
                            dataView: {readOnly: false},
                            magicType: {type: ["line", "bar"]},
                            restore: {},
                            saveAsImage: {}
                        }
                    },
                    xAxis: {
                        type: "category",
                        boundaryGap: false,
                        data: ["1", "2", "3", "4", "5", "6", "7", "8"],
                        name: "治疗时间（周）",
                        nameLocation: "middle",
                        nameTextStyle: {
                            padding: 14,
                            fontSize: 14
                        }
                    },
                    yAxis: {
                        type: "value",
                        name: "肿瘤面积",
                        nameTextStyle: {
                            padding: 4,
                            fontSize: 14
                        },
                        max: 1800
                    },
                    series: [
                        {
                            name: "面积",
                            type: "bar",
                            data: []
                        }
                    ]
                });
                myChart_perimeter.setOption({
                    title: {
                        text: "肿瘤周长变化",
                        subtext: "Tumor Circumference Change",
                        left: "center"
                    },
                    legend: {
                        data: [""]
                    },
                    tooltip: {},

                    grid: {
                        //显示数据的图表位于当前canvas的坐标轴
                        x: 50,
                        y: 55,
                        x2: 50,
                        y2: 60,
                        borderWidth: 1
                    },

                    toolbox: {
                        show: true,
                        feature: {
                            dataZoom: {
                                yAxisIndex: "none"
                            },
                            dataView: {readOnly: false},
                            magicType: {type: ["line", "bar"]},
                            restore: {},
                            saveAsImage: {}
                        }
                    },
                    xAxis: {
                        type: "category",
                        boundaryGap: false,
                        data: ["1", "2", "3", "4", "5", "6", "7", "8"],
                        name: "治疗时间（周）",
                        nameLocation: "middle",
                        nameTextStyle: {
                            padding: 14,
                            fontSize: 14
                        }
                    },
                    yAxis: {
                        type: "value",
                        name: "肿瘤周长",
                        nameTextStyle: {
                            padding: 4,
                            fontSize: 14
                        },
                        max: 400
                    },
                    series: [
                        {
                            name: "周长",
                            type: "bar",
                            data: []
                        }
                    ]
                });
            },
            // 创建模板下载链接
            downloads(data, name) {
                if (!data) {
                    return;
                }
                let url = window.URL.createObjectURL(new Blob([data]));
                let link = document.createElement("a");
                link.style.display = "none";
                link.href = url;
                link.setAttribute("download", `肿瘤CT图文件.zip`);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            },
            welcome() {
                axios({
                    method: "get",
                    url:
                        "https://cso1-1254043908.cos.ap-beijing.myqcloud.com/ct/testfile.7z",
                    responseType: "blob"
                }).then(res => {
                    this.downloads(res.data, res.headers.filename);
                    if (res.status === 200) {
                        this.$message({
                            message: "下载成功",
                            type: "success"
                        });
                        this.centerDialogVisible = false;
                        this.next();
                    } else {
                        this.$message({
                            showClose: true,
                            message: "下载失败，请重试",
                            type: "error"
                        });
                    }
                });
            },
            notice1() {
                this.$notify({
                    title: "预测成功",
                    message:
                        "点击图片可以查看大图，图片下方会显示肿瘤区域的一些特征值来供医生参考，辅助诊断",
                    duration: 0,
                    type: "success"
                });
            }
        },
        mounted() {
            this.drawChart();
        }
    };
</script>

<style>
    .el-button {
        padding: 12px 20px !important;
    }

    #hello p {
        font-size: 15px !important;
        /*line-height: 25px;*/
    }

    .n1 .el-step__description {
        padding-right: 20%;
        font-size: 14px;
        line-height: 20px;
        /* font-weight: 400; */
    }
</style>

<style scoped>
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    .dialog_info {
        margin: 20px auto;
    }

    .text {
        font-size: 14px;
    }

    .item {
        margin-bottom: 18px;
    }

    .clearfix:before,
    .clearfix:after {
        display: table;
        content: "";
    }

    .clearfix:after {
        clear: both;
    }

    .box-card {
        width: 680px;
        height: 200px;
        border-radius: 8px;
        margin-top: -20px;
    }

    .divider {
        width: 50%;
    }

    #CT {
        display: flex;
        height: 100%;
        width: 70%;
        flex-wrap: wrap;
        justify-content: center;
        margin: 0 auto;
        margin-right: 0px;
        max-width: 1200px;
        /* background-color: RGB(239, 249, 251); */
        /* box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04); */
    }

    #CT_image_1 {
        width: 90%;
        height: 40%;
        /* background-color: RGB(239, 249, 251); */
        margin: 0px auto;
        padding: 0px auto;
        /* box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04); */
        margin-right: 180px;
        margin-bottom: 0px;
        border-radius: 4px;
    }

    #CT_image {
        margin-bottom: 60px;
        margin-left: 30px;
        margin-top: 5px;
    }

    .image_1 {
        width: 275px;
        height: 260px;
        background: #ffffff;
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    }

    .img_info_1 {
        height: 30px;
        width: 275px;
        text-align: center;
        background-color: #21b3b9;
        line-height: 30px;
    }

    .demo-image__preview1 {
        width: 250px;
        height: 290px;
        margin: 20px 60px;
        float: left;
    }

    .demo-image__preview2 {
        width: 250px;
        height: 290px;

        margin: 20px 460px;
        /* background-color: green; */
    }

    .error {
        margin: 100px auto;
        width: 50%;
        padding: 10px;
        text-align: center;
    }

    .block-sidebar {
        position: fixed;
        display: none;
        left: 50%;
        margin-left: 600px;
        top: 350px;
        width: 60px;
        z-index: 99;
    }

    .block-sidebar .block-sidebar-item {
        font-size: 50px;
        color: lightblue;
        text-align: center;
        line-height: 50px;
        margin-bottom: 20px;
        cursor: pointer;
        display: block;
    }

    div {
        display: block;
    }

    .block-sidebar .block-sidebar-item:hover {
        color: #187aab;
    }

    .download_bt {
        padding: 10px 16px !important;
    }

    #upfile {
        width: 104px;
        height: 45px;
        background-color: #187aab;
        color: #fff;
        text-align: center;
        line-height: 45px;
        border-radius: 3px;
        box-shadow: 0 0 2px 0 rgba(0, 0, 0, 0.1), 0 2px 2px 0 rgba(0, 0, 0, 0.2);
        color: #fff;
        font-family: "Source Sans Pro", Verdana, sans-serif;
        font-size: 0.875rem;
    }

    .file {
        width: 200px;
        height: 130px;
        position: absolute;
        left: -20px;
        top: 0;
        z-index: 1;
        -moz-opacity: 0;
        -ms-opacity: 0;
        -webkit-opacity: 0;
        opacity: 0; /*css属性&mdash;&mdash;opcity不透明度，取值0-1*/
        filter: alpha(opacity=0);
        cursor: pointer;
    }

    #upload {
        position: relative;
        margin: 0px 0px;
    }

    #download {
        padding: 0px;
        margin: 0px 0px;
    }

    .patient {
        margin: 50px auto;
        margin-bottom: 100px;
        /* margin-right: 100px; */
        background-color: #187aab;
        border-radius: 5px;
        box-shadow: 0 0 2px 0 rgba(0, 0, 0, 0.1), 0 2px 2px 0 rgba(0, 0, 0, 0.2);
        color: #fff;
        font-family: "Source Sans Pro", Verdana, sans-serif;
        font-size: 0.875rem;
        line-height: 1;
        padding: 0.75rem 1.5rem;
    }

    #Content {
        width: 85%;
        height: 800px;
        background-color: #ffffff;
        margin: 15px auto;
        display: flex;
        min-width: 1200px;
        /* border: 1px solid #e4e7ed; */
        /* box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04); */
    }

    #aside {
        width: 25%;
        background-color: #ffffff;
        padding: 30px;
        margin-right: 80px;
        /* background-color: RGB(239, 249, 251); */
        /* box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04); */
        height: 800px;
    }

    .divider {
        background-color: #eaeaea !important;
        height: 2px !important;
        width: 100%;
        margin-bottom: 50px;
    }

    .divider_1 {
        background-color: #ffffff;
        height: 2px !important;
        width: 100%;
        margin-bottom: 20px;
        margin: 20px auto;
    }

    .steps {
        font-family: "lucida grande", "lucida sans unicode", lucida, helvetica,
        "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif;
        color: #21b3b9;
        text-align: center;
        margin: 15px auto;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }

    .step_1 {
        /*color: #303133 !important;*/
        margin: 20px 26px;
    }

    #info_patient {
        margin-top: 10px;
        margin-right: 160px;
    }
</style>


