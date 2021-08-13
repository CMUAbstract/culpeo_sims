/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under Ultimate Liberty license
  * SLA0044, the "License"; You may not use this file except in compliance with
  * the License. You may obtain a copy of the License at:
  *                             www.st.com/SLA0044
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "app_x-cube-ai.h"

#define DVFS_SETTING_5

#ifdef DVFS_SETTING_1
#define PLLM_VAL RCC_PLLM_DIV8 
#define PLLN_VAL 8
#define FLASH_WAITS FLASH_LATENCY_0
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE2

#elif defined(DVFS_SETTING_2)
#define PLLM_VAL RCC_PLLM_DIV8 
#define PLLN_VAL 16
#define FLASH_WAITS FLASH_LATENCY_1
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE2

#elif defined(DVFS_SETTING_3)
#define PLLM_VAL RCC_PLLM_DIV8 
#define PLLN_VAL 24
#define FLASH_WAITS FLASH_LATENCY_1
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE2

#elif defined(DVFS_SETTING_4)
#define PLLM_VAL RCC_PLLM_DIV8 
#define PLLN_VAL 48
#define FLASH_WAITS FLASH_LATENCY_1
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE1
#define LOOP_COUNT 35000

#elif defined(DVFS_SETTING_5)
#define PLLM_VAL RCC_PLLM_DIV8
#define PLLN_VAL 64
#define FLASH_WAITS FLASH_LATENCY_2
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE1
#define LOOP_COUNT 46000

#elif defined(DVFS_SETTING_6)
#define PLLM_VAL RCC_PLLM_DIV4
#define PLLN_VAL 75
#define FLASH_WAITS FLASH_LATENCY_4
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE1

#elif defined(DVFS_SETTING_7)
#define PLLM_VAL RCC_PLLM_DIV4
#define PLLN_VAL 85
#define FLASH_WAITS FLASH_LATENCY_4
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE1_BOOST

#elif defined(DVFS_SETTING_8)
#define PLLM_VAL RCC_PLLM_DIV8 
#define PLLN_VAL 32
#define FLASH_WAITS FLASH_LATENCY_1
#define REG_VOLTAGE PWR_REGULATOR_VOLTAGE_SCALE1

#endif

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
CRC_HandleTypeDef hcrc;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
void SystemClock_Decrease(void);
static void MX_CRC_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
static GPIO_InitTypeDef  GPIO_InitStruct;

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();
	
	__HAL_RCC_GPIOA_CLK_ENABLE();

  /* USER CODE BEGIN Init */
  SystemClock_Config();
  

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {

	GPIO_InitStruct.Pin = GPIO_PIN_8;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
	
	HAL_NVIC_SetPriority(EXTI9_5_IRQn, 2, 0);
 	HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);

	SystemClock_Decrease();
	HAL_SuspendTick();

	// Enter Sleep Mode, wake up is done once User push-button is pressed *
	HAL_PWR_EnterSLEEPMode(PWR_LOWPOWERREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    
	HAL_PWREx_DisableLowPowerRunMode();


  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */
	//__HAL_RCC_GPIOA_CLK_ENABLE();
	//GPIO_InitStruct.Pin = GPIO_PIN_8;
	//GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
	//GPIO_InitStruct.Pull  = GPIO_PULLUP;
	//GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  	//HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
 	//HAL_RCC_MCOConfig(RCC_MCO1, RCC_MCO1SOURCE_SYSCLK, RCC_MCODIV_1);
	
	GPIO_InitStruct.Pin = GPIO_PIN_9;
	GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull  = GPIO_PULLUP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_9, GPIO_PIN_SET);	
  //MX_CRC_Init();
  //MX_X_CUBE_AI_Init();
  ///* USER CODE BEGIN 2 */
  //  //HAL_GPIO_WritePin(GPIOA, GPIO_PIN_9, GPIO_PIN_SET);	
  //MX_X_CUBE_AI_Process();
	
	for( uint16_t i = 0; i < LOOP_COUNT; i++ ){
		volatile int a = 10 * 50;
		volatile int b = a + 2000;
	}

	
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_9, GPIO_PIN_RESET);	
    /* USER CODE END WHILE */
	//SystemClock_Decrease();
	//HAL_SuspendTick();

	//// Enter Sleep Mode, wake up is done once User push-button is pressed *
	//HAL_PWR_EnterSLEEPMode(PWR_LOWPOWERREGULATOR_ON, PWR_SLEEPENTRY_WFI);

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  // HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST);
  // HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1);
  // HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE2);
  HAL_PWREx_ControlVoltageScaling(REG_VOLTAGE);


  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI; 		// HSI is set to 16MHz
  RCC_OscInitStruct.PLL.PLLM = PLLM_VAL; 				// PLLM sets VCO input to 2MHz
  RCC_OscInitStruct.PLL.PLLN = PLLN_VAL; 							// VCO output = 4MHz (VCO input) * PLLN; PLLN = main sys * 2 / 4MHz
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2; 				// Main system clock = VCO output/2
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_WAITS) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief CRC Initialization Function
  * @param None
  * @retval None
  */
static void MX_CRC_Init(void)
{

  /* USER CODE BEGIN CRC_Init 0 */

  /* USER CODE END CRC_Init 0 */

  /* USER CODE BEGIN CRC_Init 1 */

  /* USER CODE END CRC_Init 1 */
  hcrc.Instance = CRC;
  hcrc.Init.DefaultPolynomialUse = DEFAULT_POLYNOMIAL_ENABLE;
  hcrc.Init.DefaultInitValueUse = DEFAULT_INIT_VALUE_ENABLE;
  hcrc.Init.InputDataInversionMode = CRC_INPUTDATA_INVERSION_NONE;
  hcrc.Init.OutputDataInversionMode = CRC_OUTPUTDATA_INVERSION_DISABLE;
  hcrc.InputDataFormat = CRC_INPUTDATA_FORMAT_BYTES;
  if (HAL_CRC_Init(&hcrc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN CRC_Init 2 */

  /* USER CODE END CRC_Init 2 */

}

/* USER CODE BEGIN 4 */
void SystemClock_Decrease(void)
{
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};

  /* Select HSI as system clock source */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_SYSCLK;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  if(HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    /* Initialization Error */
    Error_Handler();
  }

  /* Modify HSI to HSI DIV8 */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if(HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    /* Initialization Error */
    Error_Handler();
  }
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
