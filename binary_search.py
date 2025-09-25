def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def main():
    # 测试用例
    test_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    test_targets = [3, 7, 11, 1, 10]
    
    print("二分查找算法测试:")
    print(f"测试数组: {test_array}")
    print()
    
    for target in test_targets:
        result = binary_search(test_array, target)
        if result != -1:
            print(f"查找 {target}: 找到，位置在索引 {result}")
        else:
            print(f"查找 {target}: 未找到")

if __name__ == "__main__":
    main()