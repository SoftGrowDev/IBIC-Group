/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class FreightDashboard extends Component {
  setup() {
    this.action = useService("action");
    this.orm = useService("orm");

    this.state = useState({
      freightStats: {
        'air': 0,
        'ocean': 0,
        'land': 0,
        'direct_count': 0,
        'house_count': 0,
        'master_count': 0,
        'pending_booking': 0,
        'total_port': 0,
        'total_packages': 0,
      },
    });

    useSubEnv({
      config: {
        ...this.env.config,
      },
    });
    this.freightStages = useRef('freightStages');
    this.freightOperation = useRef('freightOperation');
    this.freightTransport = useRef('freightTransport');
    this.freightDirection = useRef('freightDirection');
    this.topConsignee = useRef('topConsignee');
    this.moveType = useRef('moveType');
    this.shipmentMonth = useRef('shipmentMonth');
    this.topShipper = useRef('topShipper');
    this.invoiceBill = useRef('invoiceBill');

    onWillStart(async () => {
      await loadJS('/tk_freight/static/src/js/lib/apexcharts.js');
      let freightData = await this.orm.call('dashboard.details', 'get_freight_info', []);
      if (freightData) {
        this.state.freightStats = freightData;
      }
    });

    onMounted(() => {
      this.renderFreightStages();
      this.renderFreightOperation();
      this.renderFreightTransport();
      this.renderTopConsignee();
      this.renderTopShipper();
      this.renderMoveType();
      this.renderFreightDirection();
      this.renderShipmentMonth();
      this.renderInvoiceBill();
    })
  }
  viewDashboardStatic(type) {
    let model = 'freight.shipment';
    let name;
    let domain = [];
    if (type == 'air') {
      name = 'Air Shipment'
      domain = [['transport', '=', 'air']]
    } else if (type == 'ocean') {
      name = 'Ocean Shipment'
      domain = [['transport', '=', 'ocean']]
    } else if (type == 'land') {
      name = 'Land Shipment'
      domain = [['transport', '=', 'land']]
    } else if (type == 'house') {
      name = 'House Shipment'
      domain = [['operation', '=', 'house']]
    } else if (type == 'direct') {
      name = 'Direct Shipment'
      domain = [['operation', '=', 'direct']]
    } else if (type == 'master') {
      name = 'Master Shipment'
      domain = [['operation', '=', 'master']]
    } else if (type == 'pending_booking') {
      name = 'Pending Booking'
      model = 'shipment.freight.booking'
      domain = [['state', '=', 'draft']]
    } else if (type == 'port') {
      name = 'Ports'
      model = 'freight.port'
      domain = []
    } else if (type == 'package') {
      name = 'Packages'
      model = 'freight.package'
      domain = []
    }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: name,
      res_model: model,
      view_mode: 'kanban',
      views: [[false, 'list'], [false, 'form']],
      target: 'current',
      context: { 'create': false },
      domain: domain,
    });
  }

  renderFreightStages() {
    const options = {
      series: [{
        name: "Shipments",
        data: this.state.freightStats['shipment_stages'][1]
      }],
      chart: {
        height: 350,
        type: 'bar',
        events: {
          click: function (chart, w, e) {
          }
        }
      },
      colors: ['#ff9999', '#99ff99', '#facd60', '#7EC8E3', '#1ac0c6'],
      plotOptions: {
        bar: {
          columnWidth: '45%',
          distributed: true,
        }
      },
      dataLabels: {
        enabled: false
      },
      legend: {
        show: false
      },
      xaxis: {
        categories: this.state.freightStats['shipment_stages'][0],
        labels: {
          style: {
            colors: '#000C66',
            fontSize: '12px'
          }
        }
      }
    };
    this.renderGraph(this.freightStages.el, options);
  }
  renderFreightOperation() {
    const options = {
      title: {
        text: 'Operations'
      },
      series: [{
        name: "Shipments",
        data: this.state.freightStats['fright_operation'][0]
      }],
      chart: {
        type: 'bar',
        height: 410
      },
      plotOptions: {
        bar: {
          borderRadius: 4,
          distributed: true,
        }
      },
      dataLabels: {
        enabled: false,
      },
      colors: ['#B4F8C8', '#A0E7E5', '#FFAEBC'],
      xaxis: {
        categories: this.state.freightStats['fright_operation'][1],
      },
    };
    this.renderGraph(this.freightOperation.el, options);
  }
  renderFreightTransport() {
    const options = {
      series: this.state.freightStats['transport'][1],
      chart: {
        type: 'donut',
        height: 410
      },
      colors: ['#6dd5ed', '#06beb6', '#b9e769'],
      dataLabels: {
        enabled: false
      },
      labels: this.state.freightStats['transport'][0],
      legend: {
        position: 'bottom',
      },

    };
    this.renderGraph(this.freightTransport.el, options);
  }
  renderFreightDirection() {
    const options = {
      series: this.state.freightStats['freight_direction'][1],
      chart: {
        type: 'donut',
        height: 410
      },
      colors: ['#6dd5ed', '#06beb6'],
      dataLabels: {
        enabled: false
      },
      labels: this.state.freightStats['freight_direction'][0],
      legend: {
        position: 'bottom',
      },
    };
    this.renderGraph(this.freightDirection.el, options);
  }
  renderTopConsignee() {
    const options = {
      series: [{
        name: "Amount",
        data: this.state.freightStats['top_consign'][1]
      }],
      chart: {
        height: 350,
        type: 'bar',
        events: {
          click: function (chart, w, e) {
          }
        }
      },
      colors: ['#f29e4c', '#f1c453', '#efea5a', '#b9e769', '#83e377', '#16db93', '#0db39e', '#048ba8', '#2c699a', '#54478c'],
      plotOptions: {
        bar: {
          columnWidth: '45%',
          distributed: true,
        }
      },
      dataLabels: {
        enabled: false
      },
      legend: {
        show: false
      },
      xaxis: {
        categories: this.state.freightStats['top_consign'][0],
        labels: {
          style: {
            colors: '#000C66',
            fontSize: '12px'
          }
        }
      }
    };
    this.renderGraph(this.topConsignee.el, options);
  }
  renderMoveType() {
    const options = {
      series: this.state.freightStats['move_type'][1],
      chart: {
        height: 410,
        type: 'polarArea'
      },
      labels: this.state.freightStats['move_type'][0],
      fill: {
        opacity: 1
      },
      stroke: {
        width: 1,
        colors: ['#46C2CB', '#54478c', '#0db39e', '#b9e769', '#83e377', '#16db93', '#D09CFA', '#048ba8', '#2c699a', '#FFFFD0'],
      },
      yaxis: {
        show: false
      },
      legend: {
        position: 'bottom'
      },
      theme: {
        colors: ['#46C2CB', '#54478c', '#0db39e', '#b9e769', '#83e377', '#16db93', '#D09CFA', '#048ba8', '#2c699a', '#FFFFD0'],
      }
    };
    this.renderGraph(this.moveType.el, options);
  }
  renderShipmentMonth() {
    const options = {
      series: [{
        name: 'Air',
        data: this.state.freightStats['get_shipment_month'][1]
      }, {
        name: 'Ocean',
        data: this.state.freightStats['get_shipment_month'][3]
      }, {
        name: 'Land',
        data: this.state.freightStats['get_shipment_month'][2]
      }],
      chart: {
        type: 'bar',
        height: 350,
        stacked: true,
        toolbar: {
          show: true
        },
        zoom: {
          enabled: true
        }
      },
      responsive: [{
        breakpoint: 480,
        options: {
          legend: {
            position: 'bottom',
            offsetX: -10,
            offsetY: 0
          }
        }
      }],
      plotOptions: {
        bar: {
          horizontal: false,
          borderRadius: 10,
          dataLabels: {
            total: {
              enabled: true,
              style: {
                fontSize: '13px',
                fontWeight: 900
              }
            }
          }
        },
      },
      xaxis: {
        categories: this.state.freightStats['get_shipment_month'][0]
      },
      legend: {
        position: 'right',
        offsetY: 40
      },
      fill: {
        opacity: 1
      }
    };
    this.renderGraph(this.shipmentMonth.el, options);
  }
  renderTopShipper() {
    const options = {
      series: [{
        name: "Shipments",
        data: this.state.freightStats['top_shipper'][1]
      }],
      chart: {
        height: 350,
        type: 'bar'
      },
      colors: ['#f29e4c', '#f1c453', '#efea5a', '#b9e769', '#83e377', '#16db93', '#0db39e', '#048ba8', '#2c699a', '#54478c'],
      plotOptions: {
        bar: {
          columnWidth: '45%',
          distributed: true,
        }
      },
      dataLabels: {
        enabled: false
      },
      legend: {
        show: false
      },
      xaxis: {
        categories: this.state.freightStats['top_shipper'][0],
        labels: {
          style: {
            colors: '#000C66',
            fontSize: '12px'
          }
        }
      }
    };
    this.renderGraph(this.topShipper.el, options);
  }
  renderInvoiceBill() {
    const options = {
      series: [{
        name: 'Bills',
        data: this.state.freightStats['get_bill_invoice'][1]
      }, {
        name: 'Invoice',
        data: this.state.freightStats['get_bill_invoice'][2]
      }],
      chart: {
        type: 'bar',
        height: 350,
        stacked: true,
        toolbar: {
          show: true
        },
        zoom: {
          enabled: true
        }
      },
      responsive: [{
        breakpoint: 480,
        options: {
          legend: {
            position: 'bottom',
            offsetX: -10,
            offsetY: 0
          }
        }
      }],
      plotOptions: {
        bar: {
          horizontal: false,
          borderRadius: 10,
          dataLabels: {
            total: {
              enabled: true,
              style: {
                fontSize: '13px',
                fontWeight: 900
              }
            }
          }
        },
      },
      xaxis: {
        categories: this.state.freightStats['get_bill_invoice'][0]
      },
      legend: {
        position: 'right',
        offsetY: 40
      },
      fill: {
        opacity: 1
      }
    };

    this.renderGraph(this.invoiceBill.el, options);
  }

  renderGraph(el, options) {
    const graphData = new ApexCharts(el, options);
    graphData.render();
  }
}
FreightDashboard.template = "tk_freight.template_freight_dashboard";
registry.category("actions").add("freight_dashboard", FreightDashboard);