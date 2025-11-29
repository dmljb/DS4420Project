// import {
//     Chart as ChartJS,
//     CategoryScale,
//     LinearScale,
//     PointElement,
//     LineElement,
//     Title,
//     Tooltip,
//     Legend,
//   } from 'chart.js';
//   import { Line } from 'react-chartjs-2';
  
//   ChartJS.register(
//     CategoryScale,
//     LinearScale,
//     PointElement,
//     LineElement,
//     Title,
//     Tooltip,
//     Legend
//   );

// interface YieldCurveData {
//     maturities: number[];
//     rates: number[];
//   //   curve_type: string;
//   }
  
//   interface Props {
//     data: YieldCurveData;
//   }

//   const YieldCurveChart: React.FC<Props> = ({ data }) => {
//     const chartData = {
//       labels: data.maturities.map(m => `${m}Y`),
//       datasets: [{
//       //   label: data.curve_type,
//         data: data.rates,
//       }]
//     };

//     return <Line data={chartData} />;
//   };
  
//   export const options = {
//     responsive: true,
//     plugins: {
//       legend: {
//         position: 'top' as const,
//       },
//       title: {
//         display: true,
//         text: 'Current Yield Curve',
//       },
//     },
//   };
  
//   export default YieldCurveChart;

//   export function App() {
//     return <Line options={options} data={} />;
//   }

  


import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
  } from 'chart.js';
  import { Line } from 'react-chartjs-2';
  import { faker } from '@faker-js/faker';
  
  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  );
  
  export const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Chart.js Line Chart',
      },
    },
  };
  
  const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];
  
  export const data = {
    labels,
    datasets: [
      {
        label: 'Dataset 1',
        data: labels.map(() => faker.number.int({ min: -1000, max: 1000 })),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Dataset 2',
        data: labels.map(() => faker.number.int({ min: -1000, max: 1000 })),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  };
  
  export function App() {
    return <Line options={options} data={data} />;
  }