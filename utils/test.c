#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

#define ARRAY_SIZE (128 * 128)  // Size of the array (1M elements)
#define STRIDE 64  // Access stride to create conflict misses (tune this value)

int main() {
    // Allocate a large array
    int *array = (int *)malloc(ARRAY_SIZE * sizeof(int));
    if (array == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return -1;
    }

    // Initialize the array
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = i;
    }

    // Start the cache conflict stressing loop
    clock_t start_time = clock();

    // Perform memory accesses with a large stride to create cache conflicts
    for (int i = 0; i < 100; i++) {  // Large number of iterations to stress the cache
        for (int j = 0; j < ARRAY_SIZE; j += STRIDE) {
            // Access array elements with a stride
            int temp = array[j];
        }
    }

    clock_t end_time = clock();

    // Print time taken for the operation
    double elapsed_time = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;
    printf("Cache conflict stress test completed in %.2f seconds\n", elapsed_time);

    // Clean up
    free(array);
    return 0;
}
